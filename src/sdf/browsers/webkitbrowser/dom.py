# *- coding: utf-8 -*
'''
Created on 10/07/2009

@author: Ignacio Avas
'''

from .domelement import DomElement
from sdf.exception import JavaScriptError
from time import time
from PyQt4.QtCore import QObject
import json
from .. import dom
from threading import Lock

class DOM(QObject, dom.DOM):
	"""
	Una clase que representa el DOM, es abstracta y necesita que se
	implementen ciertos métodos.
	"""
	
	# el nombre del variables que tiene almacenado el DOM
	__var_dict_name = "__webkit_domvars__"
	__var_dict_count = 0 # un contador para ver las variables creadas
	
	
	def __init__(self):
		QObject.__init__(self)
		dom.DOM.__init__(self)
	
	######## Métodos abstractos 
	def get_html(self):
		"Retorna el texto html del DOM actual"
		raise NotImplementedError
	
	def eval_js(self, script, throw_exceptions = False):
		"""
		Evalúa un script Javascript sobre el DOM
		Si throw_exceptions == True: tira excepciones cuando 
			el script tira excepciones al ejecutarse 
		"""
		raise NotImplementedError

	def open_link(self, posx, posy):
		"Abre el link en la posición especificada"
		raise NotImplementedError
	#########
	
	def wait_load_page(self):
		"""
		Espera hasta que la página termine de cargar.
		"""
		# Esta función no hace nada a no ser que se sobrecargue
		pass

	def get_element_by_id(self, id):
		"Devuelve el elemento con el id dado"
		js_expr = 'document.getElementById("%s")' % id
		
		# chequea que haya un elemento con ese id, por seguridad
		if self.eval_js("window.%s == undefined" % js_expr):
			raise ValueError("%s id not found" % id)
		return DomElement(js_expr, self)
	
	def get_elements_by_name(self, name):
		"Devuelve una lista con todos los elementos con el nombre dado"
		
		# forma la expresión
		script = 'document.getElementsByName("%s").length' % name
		# la convierte a entero
		length = int(self.eval_js(script))
		res = [] # forma el resultado
		for i in range(length): # forma un elemento por cada elemento del arreglo
			expr = 'document.getElementsByName("%s")[%d]' % (name, i)
			# la pone en las variables fijas de la ventana
			new_expr = self.__register_var_js(expr) 
			res.append(DomElement(new_expr, self))
		return res
	
	def get_elements_by_xpath(self, xpath, element = None):
		"Obtiene todos los elementos que cumplen con el xpath dado"
		new_elements = self.__register_var_js_xpath(xpath, element)
		return [ DomElement(expr, self) for expr in new_elements ]
		

	def __register_var_js_xpath(self, xpath, element = None):
		"""
		Registra todas los elementos que coincidan con cierto xpath y
		devuelve una lista de expresiones que hacen referencias a ellas
		"""
		if element == None:
			element_expr = 'document'
		else:
			element_expr = element.get_js_expression()
		
		# el script pone todas las variables en la colección de variables
		script = """
		if(window.$VAR_COLLECTION == undefined)
			window.$VAR_COLLECTION = [];
	
		// busca los elementos con el xpath indicado
		var __webkit_xpath_res = document.evaluate($XPATH_EXPR,
			$ELEMENT_EXPR, null, XPathResult.ANY_TYPE, null);
		
		var __webkit_it__ = null; // iterador en el resultado 
		var __webkit_count__ = $COUNT; // contador para agregar en el arreglo
		
		// agrega cada elemento encontrado a la colección
		while(true){
			__webkit_it__ = __webkit_xpath_res.iterateNext();
			if(__webkit_it__ == null)
				break;
			$VAR_COLLECTION[__webkit_count__] = __webkit_it__;
			++__webkit_count__;
		}
	
		// tiene la cantidad de elementos agregados que se devuelve al evaluar
		// el script
		(__webkit_count__ - $COUNT)
		"""
		
		# sustituye variables por nombres
		script = script.replace("$VAR_COLLECTION", self.__var_dict_name)
		script = script.replace("$XPATH_EXPR", json.dumps(xpath))
		script = script.replace("$COUNT", json.dumps(self.__var_dict_count))
		script = script.replace("$ELEMENT_EXPR", element_expr)
		
		# evalúa el script y saca cuantos elementos fueron encontrados
		agregados = self.eval_js(script)
		if agregados == None:
			msg = "Internal Error, check parameters or page state"
			raise JavaScriptError(msg)
		agregados = int(agregados)
		# arma la lista con las expresiones
		res = []
		for i in range(self.__var_dict_count, self.__var_dict_count + agregados):
			res.append("%s[%d]" % (self.__var_dict_name, i))
		self.__var_dict_count += agregados
		return res
		

	def __register_var_js(self, var_expr):
		"""
		Registra una variable en el DOM actual y devuelve una expresión que
		hace referencia a ella
		"""
		
		# el script que pone la variable en el arreglo
		script = """
		if(window.$VAR_COLLECTION == undefined)
			window.$VAR_COLLECTION = [];
		window.$VAR_COLLECTION[$ID] = ($EXPR);
		"""
		
		# sustituye variables por nombres
		script = script.replace("$VAR_COLLECTION", self.__var_dict_name)
		script = script.replace("$ID", str(self.__var_dict_count))
		script = script.replace("$EXPR", var_expr)
		
		# ejecuta el script propiamente dicho
		self.eval_js(script)
		res = "window.%s[%d]" % (self.__var_dict_name, self.__var_dict_count)
		self.__var_dict_count += 1
		return res 
