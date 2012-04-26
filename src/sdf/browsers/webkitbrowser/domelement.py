# *- coding: utf-8 -*
'''
Created on 10/07/2009

@author: Ignacio Avas
'''

import json
from .. import domelement
from sdf.exception import OldElementError
from sdf.browsers.browser import PreloadPageListener

class DomElement(domelement.DomElement):
	"""
	Modela un objeto del dom, es una interface para acceder a un objeto y
	hacer acciones con él.
	El elemento tiene una expresión en javascript  que hace referencia a él
	"""
	
	def __init__(self, js_expresion, dom):
		'''
		Construye un elemento de un DOM
		js_expression -- la expresión en Javascript que devuelve a este objeto
		dom -- el DOM que contiene al objeto
		'''
		domelement.DomElement.__init__(self)
		dom.subscribe_preload_page(_PreloadPageListener(self))
		self.__element = _JavascriptDomElement(js_expresion, dom)
		self.__invalid = False
				
	def invalidate(self):
		# invalida al elemento
		self.__invalid = True	
		self.__element = _InvalidDomElement()
	
	def get_js_expression(self):
		return self.__element.get_js_expression()
				
	def set_value(self, val):
		return self.__element.set_value(val)
		
	def get_value(self):
		return self.__element.get_value()
				
	def click(self, wait_load_page = False):
		return self.__element.click(wait_load_page)
		
	def get_pos(self):
		return self.__element.get_pos()

	def get_tag_name(self):
		return self.__element.get_tag_name()
		
	def get_property(self, property_name):
		return self.__element.get_property(property_name)
	
	def get_attributes(self):
		return self.__element.get_attributes()
		
	def get_parent(self):
		return self.__element.get_parent()
	
	def get_elements_by_xpath(self, xpath):
		return self.__element.get_elements_by_xpath(xpath)

	def get_html(self):
		return self.__element.get_html()

	def __getattr__(self, attr):
		return self.__element.__getattr__(attr)


class _InvalidDomElement(object):
	"El elemento DOM que modela un elemento inválido de una página que se cargó"
	
	def get_js_expression(self):
		raise OldElementError("Invalid element of old page")
				
	def set_value(self, val):
		raise OldElementError("Invalid element of old page")
		
	def get_value(self):
		raise OldElementError("Invalid element of old page")
				
	def click(self, wait_load_page = False):
		raise OldElementError("Invalid element of old page")
		
	def get_pos(self):
		raise OldElementError("Invalid element of old page")

	def get_tag_name(self):
		raise OldElementError("Invalid element of old page")
		
	def get_property(self, property_name):
		raise OldElementError("Invalid element of old page")
	
	def get_attributes(self):
		raise OldElementError("Invalid element of old page")
		
	def get_parent(self):
		raise OldElementError("Invalid element of old page")
	
	def get_elements_by_xpath(self, xpath):
		raise OldElementError("Invalid element of old page")

	def get_html(self):
		raise OldElementError("Invalid element of old page")

	
class _JavascriptDomElement(DomElement):
	def __init__(self, js_expresion, dom):
		'''
		Construye un elemento de un DOM
		js_expression -- la expresión en Javascript que devuelve a este objeto
		dom -- el DOM que contiene al objeto
		'''
		domelement.DomElement.__init__(self)
		self.__js_expresion = js_expresion
		self.__dom = dom

	def get_js_expression(self):
		"""
		Retorna una expresión de javascript que hace referencia al elemento
		Se puede usar para hacer una evaluación en el DOM con javascript 
		"""
		return self.__js_expresion
				
	def set_value(self, val):
		"pone el valor del campo value del elemento en un valor fijo"
		str_val = json.dumps(val)
		expresion_final = "%s.value = %s" % (self.__js_expresion, str_val)
		self.__eval_js(expresion_final)
		
	def get_value(self):
		"devuelve el valor del campo value del elemento"
		expresion_final = "%s.value" % (self.__js_expresion)
		return self.__eval_js(expresion_final)
		
		
	def click(self, wait_load_page = False, throw_exception = True):
		"""
		Hace un click al elemento: invoca a click().
		Si wait_load_page es True espera hasta terminar de cargar la página.
		Util para los links
		"""
		
		if self.get_tag_name().lower() == 'option':
			script = """
			var __webkit_evt = document.createEvent("HTMLEvents");
			__webkit_evt.initEvent("change", true, true );
			$ELEMENT.parentElement.value = $ELEMENT.value
			$ELEMENT.parentElement.dispatchEvent(__webkit_evt);
			"""
			script = script.replace("$ELEMENT", self.__js_expresion)
		else:
			script = """
			var __webkit_evt = document.createEvent("MouseEvents");
			__webkit_evt.initMouseEvent("click", true, true, window, 
				0, 0, 0, 0, 0, false, false, false, false, 0, null);
			%s.dispatchEvent(__webkit_evt); 
			""" % self.__js_expresion
			
			
		self.__eval_js(script, throw_exception = throw_exception)
					
		if wait_load_page: # espera a que termine de cargar
			self.__dom.wait_load_page()
		
	
	def get_pos(self):
		"Devuelve (x, y) la posición del elemento"
		# Obtiene la posición del objeto
		script = """
		__webkit_x_pos = __webkit_y_pos = 0;
		__webkit_var = $OBJ
		while(__webkit_var.offsetParent != null) {
			__webkit_x_pos += __webkit_var.offsetLeft;
			__webkit_y_pos += __webkit_var.offsetTop;
			__webkit_var = __webkit_var.offsetParent;
		}
		"""
		script = script.replace("$OBJ", self.__js_expresion)
		self.__eval_js(script)

		xpos = self.__eval_js('__webkit_x_pos')
		ypos = self.__eval_js('__webkit_y_pos')
		return xpos, ypos


	def get_tag_name(self):
		"Obtiene el nombre del tag"
		return self.get_property("tagName")
		
	def __eval_js(self, script, throw_exception = True):
		"evalúa un script en el frame del elemento"
		return self.__dom.eval_js(script, throw_exception)
	
	def get_property(self, property_name):
		"Obtiene una propiedad del elemento"
		return self.__eval_js("%s.%s" %(self.__js_expresion, property_name))
	
	def get_attributes(self):
		"""
		Devuelve un diccionario con los nombres de los atributos y sus valores
		"""
		res = {}
		script = "%s.attributes.length" % self.__js_expresion
		for i in range(int(self.__eval_js(script))):
			name_expr = "%s.attributes[%s].name" % (self.__js_expresion, i)
			name = self.__eval_js(name_expr)
			value_expr = "%s.attributes[%s].value" % (self.__js_expresion, i)
			value = self.__eval_js(value_expr)
			res[name] = value
		return res

	def get_parent(self):
		return DomElement("(%s).parentNode" % (self.__js_expresion), self.__dom)
	
	def get_elements_by_xpath(self, xpath):
		"Obtiene todos los elementos que cumplen con el xpath dado"
		return self.__dom.get_elements_by_xpath(xpath, self)

	def get_html(self):
		"Devuelve un string con la representación de la página" 
		return self.get_property('innerHTML')

	def __getattr__(self, attr):
		return self.get_property(attr)
	

class _PreloadPageListener(PreloadPageListener):
	"Modela un escucha de carga de la página"
	def __init__(self, dom_element):
		PreloadPageListener.__init__(self)
		self.__dom_element = dom_element
	
	def on_load_page(self, browser):
		"Se llama al cargar una página"
		browser.unsubscribe_preload_page(self)
		self.__dom_element.invalidate()
	
	