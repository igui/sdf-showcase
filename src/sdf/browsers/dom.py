# *- encoding: utf-8 -*
'''
Created on 20/08/2009

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
import json
import re
from lxml import html, etree, cssselect
from threading import Lock


class DOM(object):
	'''
	Interfaz para representar un DOM
	'''

	def __init__(self):
		self.__preload_page_subscribers_lock = Lock()
		self.__preload_page_subscribers = []
	
	def find(self,
			attribute = None,
			class_name = None,
			id = None,
			name = None,
			tag = None,
			text = None,
			text_contains = None,
			re_test = None,
			xpath = None,
			css = None
		):
		"Igual a :func:`find_many` pero devuelve un solo elemento a lo sumo"
		res = self.find_many(attribute, class_name, id, name, tag, text, text_contains, re_test ,xpath, css)
		if len(res) == 0:
			return None
		else:
			return res[0]
	
	def find_many(self,
			attribute = None,
			class_name = None,
			id = None,
			name = None,
			tag = None,
			text = None,
			text_contains = None,
			re_test = None,
			xpath = None,
			css = None
		):
		"""
		Retorna una lista de elementos que cumplen con un conjunto de 
		determinados criterios de búsqueda. Los criterios se definen usando
		keywords:
		
		*class_name*
			si tiene un clase dada 
		*attribute*
			attribute puede ser de tres tipos:
				1. str o unicode: Se busca un elemento con un atributo del tipo indicado.
				2. list: Se busca un elemento que contenga todos los atributos especificados en la lista.
				3. dict: Se busca un elemento que contenga todos los atributos especificados y que ademas 
						los valores de los mismos coincidan con los valores indicados por el diccionario.
					
			Si se tiene el siguiente código
			
			.. code-block:: html
			
				<html><body>
					<a href='spam' rel='bar'/>
					<a href='eggs' src='foo'/>
					<a href='eggs' src='toast'/>
				</body></html>

			Suponiendo que browser cargó esa página ::	
				
				browser.find_many(tag = 'a', attribute = 'rel')                                # devuelve el primer a
				browser.find_many(tag = 'a', attribute = [ 'href', 'src' ])                    # devuelve el segundo y el tercer a 
				browser.find_many(tag = 'a', attribute = { 'href' : 'eggs', 'src' : 'toast' }) # devuelve el tercero 
			
		*id*
			si tiene el id en un valor determinado
		*name*
			si tiene el atributo name definido con cierto valor
		*tag*
			si tiene un en la de elemento dado: 'A', 'H1', etc. 
		*text*
			si tiene algún texto en particular
		*text_contains*
			si el texto contiene alguna cadena particular
		*re_test*
			busca que un atributo coincida con una expresión regular
			se deben pasar pares (<nombre atributo>, expresión regular)
		*xpath*
			Excluyente a todos los otros: Obtiene por xpath absoluto
		*css*
			Excluyente a todos los otros: Obtiene por selector CSS
			
		"""
		for i in (attribute, class_name, id, name, tag, text, xpath, css):
			if i == None:
				break
		else:
			raise ValueError("You must specify at least one parameter")
		
		# se eligió búsqueda por css
		if css != None:
			for i in (attribute, class_name, id, name, tag, text, xpath,
					text_contains, re_test):
				if i != None:
					raise ValueError("You must either specify xpath, css or "\
					 "other parameter but not both")

			return self.get_elements_by_xpath(cssselect.css_to_xpath(css))
		
		# se eligió búsqueda por xpath
		if xpath != None:
			for i in (attribute, class_name, id, name, tag, text,
					text_contains, re_test):
				if i != None:
					raise ValueError("You must either specify xpath, css or "\
					 "other parameter but not both")
			return self.get_elements_by_xpath(xpath)
		
		# computa los criterios que tienen que ver con atributos
		attr_criteria = []
		if attribute != None:
			# - 'attribute' puede ser de tres tipos:
			# 1) str, unicode: Se busca un elemento con un atributo del tipo indicado.
			# 2) list: Se busca un elemento que contenga todos los atributos especificados en la lista.
			# 3) dict: Se busca un elemento que contenga todos los atributos especificados y que ademas 
			#		  los valores de los mismos coincidan con los valores indicados por el diccionario.
			
			if isinstance(attribute, str) or isinstance(attribute, str):
				attr_criteria.append("@%s" % attribute)
			elif isinstance(attribute, list):
				for a in attribute:
					attr_criteria.append("@%s" % a)
			elif isinstance(attribute, dict):
				for k, v in attribute.items():
					attr_criteria.append("@%s=%s" % (k, json.dumps(v)))
			else:
				raise ValueError('attribute es de tipo no valido. Se esperaba: str, unicode, list o dict. Se encontro: ' + str(attribute.__class__.__name__))
		
		attr_dict = {'class':class_name, 'id':id, 'name': name }
		for attr, attr_val in list(attr_dict.items()):
			if attr_val != None:
				attr_criteria.append("@%s=%s" % (attr, json.dumps(attr_val)))
		
		# por texto
		if text != None:
			attr_criteria.append("@%s=%s" % ('text()', json.dumps(text)))
		
		if text_contains != None:
			attr_criteria.append("contains(text(), %s)" % json.dumps(text_contains))
		
		# computa cada parte de la expresión final	
		if tag == None:
			tag_expr = "*"
		else:
			tag_expr = tag
			
		if len(attr_criteria) == 0:
			attr_criteria_expr = "" 
		else:
			attr_criteria_expr = "[ %s ]" % " and ".join(attr_criteria)
		
		# computa el xpath final a evaluar
		xpath_expr = ".// %s %s" % (tag_expr, attr_criteria_expr)
		res =  self.get_elements_by_xpath(xpath_expr)

		# filtra si hay una expresión regular
		if re_test != None:
			res = self.__filter_by_re_test(res, re_test)
		
		return res 
	
	def __filter_by_re_test(self, res, re_test):
		for attribute_name in list(re_test.keys()):
			re_test[attribute_name] = re.compile(re_test[attribute_name])
			
		def matches_re_test(element):
			"""
			Retorna true sii el elemento cumple con todas las expresiones
			regulares
			"""
			for attribute_name, regexp in list(re_test.items()):
				attribute = element.get_property(attribute_name)
				if attribute == None or regexp.search(str(attribute)) == None:
					return False
			else:
				return True
				
		return list(filter(matches_re_test, res))
	
	def get_inner_text(self):
		"Devuelve el texto del html"
		try:		
			html_element = etree.HTML(self.get_html(), parser = html.HTMLParser())
		except:
			return None
		
		if html_element is None:
			return self.get_html()
			
		text = ""
		for element in html_element.iter():
			if element.tag == 'script':
				continue
			if element.text is not None:
				text += element.text 
			if element.tail is not None:
				text += element.tail

		return text
	
	
	def get_elements_by_xpath(self, xpath):
		"Obtiene todos los elementos que cumplen con el xpath dado"
		raise NotImplementedError   

	def get_html(self):
		"Devuelve un string con la representación de la página" 
		raise NotImplementedError
	
	def _on_preload(self):
		"Se debe llamar cuando se carga el DOM"
		with self.__preload_page_subscribers_lock:
			for s in self.__preload_page_subscribers:
				s.on_load_page(self)
	
	def subscribe_preload_page(self, subscriber):
		"""
		Permite suscribirse a un evento de carga de la p￡gina usando la clase
		PreloadPageListener
		"""
		from sdf.browsers.browser import PreloadPageListener
		check_if_any_type(subscriber, PreloadPageListener)
		
		with self.__preload_page_subscribers_lock:
			self.__preload_page_subscribers.append(subscriber)
			
	def unsubscribe_preload_page(self, subscriber):
		"Saca al escucha del evento de precarga de la p￡gina"
		self.__preload_page_subscribers.remove(subscriber)
		
		