# *- encoding: utf-8 -*
'''
Created on 23/07/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
from urllib.parse import urlencode

class Request(object):
	'''
	Encapsula un request de HTTP. Es usado principalmente para cargar una página
	con la función
	:func:`load_page<sdf.browsers.browser.Browser.load_page>` del
	browser. Por ejemplo: ::
	
		request = Request.post(
		                      url = 'http://www.snee.com/xml/crud/posttest.cgi',
		                      body = 'fname=nombre&lname=apellido',
		                      headers = { 'Cookie': '$Version=1; Skin=new;' }
		                      )
		browser.load_page(request)
		print browser.get_html()
	
	El constructor principal toma 4 parámetros: url, method que es el método 
	(GET o POST), body que representa el cuerpo de la petición (solo válido para
	POST) y el campo headers en el que se pueden agregar cabezales extra a la
	petición como el header Cookie.
	'''
	SupportedMethods = ('GET', 'POST')
		
	def __init__(self, url, method = 'GET', body = '', headers = {}):
		check_if_any_type(url, str)
		check_if_any_type(body, (str, dict))
		check_if_any_type(headers, dict)
				
		if method not in self.SupportedMethods:
			raise ValueError("Method must be one of the following: " % \
					', '.join(self.SupportedMethods))
		
		if isinstance(body, str):
			self.__body = body
		else:
			self.__body = urlencode(body)
		
		self.__url = url
		self.__method = method
		
		self.__headers = headers
	
	@classmethod
	def post(cls, url, body = '', headers = {}):
		"""
		Crea un POST. Equivalente a llamar a
		``Request(url, 'POST', body, headers)``
		"""
		return Request(url, 'POST', body, headers)
	
	@classmethod
	def get(cls, url, headers = {}):
		"""
		Crea un GET. Equivalente a llamar a ``Request(url, 'GET', '', headers)``
		"""
		return Request(url, 'GET', '', headers)
	
	@property
	def url(self):
		return self.__url
	
	@url.setter
	def url(self, value):
		check_if_any_type(value, str)
		self.__url = value
		
	@property
	def method(self):
		return self.__method
	
	@property
	def body(self):
		return self.__body
	
	@property
	def headers(self):
		return self.__headers
	
	def __repr__(self):
		"Retorna una representacion del request"
		if self.__method == 'GET':
			return '<GET %s>' % self.__url
		else:
			return '<%s %s body:"%s" headers:"%s">' % (
												self.__method,
												self.__body,
												self.__headers
												)