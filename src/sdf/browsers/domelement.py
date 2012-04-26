# *- encoding: utf-8 -*
'''
Created on 20/08/2009

@author: iavas
'''
import json
from . import dom
import lxml.html
import lxml.etree
from sdf.helpers.string_helper import Extractor

class DomElement(dom.DOM):
	'''
	Interfaz para representar un elemento del DOM
	'''

	def __init__(self):
		pass
		
	def get_value(self):
		"devuelve el valor del campo value del elemento"
		raise NotImplemented
		
	def click(self, wait_load_page = False):
		"""
		Hace un click al elemento o va al link donde apunta, si *wait_load_page*
		es :const:`True`, espera a que cargue la página. Esto es útil si se
		hace click en un link o en un botón de submit.
		
		Si *wait load_page* es :const:`False`, retorna inmediatamente después
		de hacer el	click, esto es util si se hace click en una lista
		desplegable o en un elemento que no recargue la página 
		"""
		raise NotImplemented
	
	def get_tag_name(self):
		"Obtiene el nombre del tag"
		raise NotImplemented
	
	def get_property(self, property_name):
		"Obtiene una propiedad del elemento"
		raise NotImplemented
	
	def get_attributes(self):
		"""
		Devuelve un diccionario con los nombres de los atributos y sus valores
		"""
		raise NotImplemented
	   
	def extract(self, pattern):
		"Extrae texto del contenido del elemento"
		return Extractor.extract(pattern, self.get_property('innerHTML'))
	
	def extract_all(self, pattern):
		"""
		Extrae texto del contenido del elemento. Versión que da todas las
		ocurrencias
		"""
		return Extractor.extract_all(pattern, self.get_property('innerHTML'))
	
	def get_parent(self):
		"Devuelve el padre del elemento"
		raise NotImplemented
			
	def __repr__(self):
		"""
		Obtiene una representación del elemento de la forma
		<tag[ atributo=valor]*>
		"""
		attributes = []
		for k, v in list(self.get_attributes().items()):
			attributes.append(" %s=%s" % (k, json.dumps(v)))
		
		return "<%s%s>" % (self.get_tag_name().lower(), ''.join(attributes))
	