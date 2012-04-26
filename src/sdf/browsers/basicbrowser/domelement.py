# *- coding: utf-8 -*
'''
Created on 21/08/2009

@author: iavas
'''
from .. import domelement
from lxml import etree

class DomElement(domelement.DomElement):
	"Un elemento de Dom para BasicBrowser"
	
	def __init__(self, htmlelement, browser):
		"Construye un domElement que actua de wrapper a un htmlelement"
		domelement.DomElement.__init__(self)
		self.__browser = browser
		self.__element = htmlelement
		self.__url = browser.get_url()
	
	def get_value(self):
		"devuelve el valor del campo value del elemento"
		return self.get_property('value')
			
	def click(self, wait_load_page = True):
		"""
		Hace un click al elemento o va al link donde apunta
		"""
		if self.__element.tag == 'a':
			self.__browser.load_page(self.get_property('href'))
		
	
	def get_tag_name(self):
		"Obtiene el nombre del tag"
		return self.__element.tag
	
	def get_property(self, property_name):
		"Obtiene una propiedad del elemento"
		if property_name.lower() == 'innerhtml':
			text_list = [ etree.tounicode(i, pretty_print = True) for i in self.__element ]
			
			if self.__element.text != None:
				text_list = [ self.__element.text ]  + text_list
			
			return ''.join(text_list) 
		else:
			res = self.__element.get(property_name)
			return res 
		
	def get_elements_by_xpath(self, xpath_expr):
		"Devuelve HTMLDomElement según un xpath dado"
		r = self.__element.xpath(xpath_expr)
		return [ DomElement(i, self.__browser) for i in r ]
	
	def get_attributes(self):
		"""
		Devuelve un diccionario con los nombres de los atributos y sus valores
		"""
		return dict(list(self.__element.items()))
	
	def get_parent(self):
		return DomElement(self.__element.getparent(), self.__browser)
	
	def get_html(self):
		"Devuelve un string con la representación de la página" 
		return self.get_property('innerHTML')
  
	def __getattr__(self, attr):
		 return self.get_property(attr)

		