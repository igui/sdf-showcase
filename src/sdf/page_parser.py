# *- encoding: utf-8 -*
'''
Created on 28/07/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type, check_if_integral
from types import NoneType, FunctionType, MethodType
from sdf import BaseParser
from numbers import Integral


class PageParser(BaseParser):
	"""
	Representa un parser el cual se puede hacer usando páginas
	"""
	
	def __init__(self, context):
		BaseParser.__init__(self, context)
		self.__context = context
		self .__page_parser_driver = None
	
	def _set_page_parser_driver(self, driver):
		"Setea el Driver para ejecutar el PageParser"
		from sdf import BasePageParserDriver
		check_if_any_type(driver, BasePageParserDriver)
		self.__page_parser_driver = driver
	
	def _run(self):
		if self.__page_parser_driver == None:
			from .local_page_parser_driver import LocalPageParserDriver
			driver = LocalPageParserDriver(self.__context, self)
			#driver = LocalPageParserDriver(self.__context)
			driver.run()
		else:
			self.__page_parser_driver.run()
		
		
	############ Métodos que pueden ser implementados en subclases ############
	
	def start(self, context):
		"""
		Se llama solo al principio del parser para agregar las páginas
		iniciales a parsear. Cuando se reanuda una corrida esta función no se
		llama ya que 
		
		oprincipalmente llama a
		:func:`context.add_page<sdf.page_parser_driver.PagingContext.add_page>`
		o
		:func:`context.add_item<sdf.page_parser_driver.PagingContext.add_item>`
		del objeto context que es de la clase
		:class:`PagingContext<sdf.page_parser_driver.PagingContext>`
		"""
		raise NotImplementedError
	
	
	def finalize(self, context, processed_items, unprocessed_items):
		"""
		Se llama al finalizar el proceso
		"""
		pass
	
	def get_paralel_num(self):
		"""
		Define la cantidad de páginas que se procesan en paralelo.
		Por defecto es 2
		"""
		return 2
	

class Page(object):
	'''
	Representa un objeto que tiene información de una página, contiene la url
	de la página y atributos extra que se le pueden pasar para almacenarlos: ::
	
	    p = Page('http://www.ham.com/page/1', categoria = 43, otra_cosa = True)
	    # equivalente a 	
	    p = Page('http://www.ham.com/page/1')
	    p.categoria = 44
	    p.otra_cosa = True
	    
	El parámetro *url* es la dirección de la página, parse es la función usada
	para parsear la página. Por defecto se usa la función de la página pero se
	puede pasar un método del ListBasedParser. El parámetro *navigate* es
	opcional y define la función usada para navegar hacia la página, por defecto
	simplemente navega a la url de la página aunque se podría poner otro
	comportamiento, por ejemplo si es necesario hacer un post, o bien si hay 
	que usar javascript.
	Si el parámetro *end_on_error* es True, si hay un error al procesar la 
	página se detiene el parseo en ese momento (util para páginas de items),
	si es False se sigue el paginado hasta el final.
	El parámetro priority es un entero tiene la prioridad de la página,
	el parser procesa las páginas con prioridad más alta es 0 y la más baja es
	999 	  
	'''
	
	# los rangos de la prioridad de las páginas
	PRIORITY_MAX = 0
	PRIORITY_MIN = 999

	def __init__(self,
				url,
				parse = None,
				navigate = None,
				end_on_error = True,
				priority = None,
				**extra_attributes
				):
		self.__url = url
		
		m, f = self.__get_func(parse)
		self.__parse_is_method = m
		self.__parse_func = [ f ]
		m, f = self.__get_func(navigate)
		self.__navigate_is_method = m
		self.__navigate_func = [ f ] 
		
		# chequea y asigna prioridad a la página
		check_if_any_type(priority, (Integral, NoneType))
		if priority == None:
			priority = self.PRIORITY_MIN
		if priority not in list(range(self.PRIORITY_MAX, self.PRIORITY_MIN+1)):
			raise ValueError("priority must be beetween %d and %d" % (
				self.PRIORITY_MAX, self.PRIORITY_MIN))
		self.__priority = priority 
				
		self.__parser_instance = None
		
		self.__end_on_error = bool(end_on_error)
		
		# setea los atributos extra
		for attribute, value in list(extra_attributes.items()):
			if not hasattr(self, attribute):
				setattr(self, attribute, value)
	
	def __get_func(self, func):
		check_if_any_type(func, (NoneType, FunctionType, MethodType))
		
		if isinstance(func, FunctionType):
			return False, func 
		elif isinstance(func, MethodType): # instancemethod
			check_if_any_type(func.__self__, PageParser)
			return True, func.__func__.__name__
		else:
			return False, None

	def _set_parser_instance(self, parser_instance):
		"Setea la instancia del parser que tiene a la página"
		self.__parser_instance = parser_instance
									
	@property
	def url(self):
		"La url de la página actual, si tiene"
		return self.__url
	
	@property
	def priority(self):
		"La prioridad de la página"
		return self.__priority
	
	@property
	def end_on_error(self):
		return self.__end_on_error
	
	def parse(self, context):
		"""
		Procesa a la página. Principalmente llama a
		:func:`context.add_page()<sdf.page_parser_driver.PagingContext.add_page>`
		o
		:func:`context.add_item()<sdf.page_parser_driver.PagingContext.add_item>`
		del objeto context que es de la clase
		:class:`PagingContext<sdf.page_parser_driver.PagingContext>`
		"""
		if self.__parse_func[0] == None:
			raise NotImplementedError
		elif not self.__parse_is_method:
			return self.__parse_func[0](context)
		else:
			getattr(self.__parser_instance, self.__parse_func[0])(context)
	
	def navigate(self, context):
		"""
		Se llama antes de llamar a :func:`parse()<sdf.page_parser.Page.parse>`.
		Se usa para definir
		como se navega a la página. Si no se define lo que se hace es navegar
		a la url directamente. El parámetro context es un objeto del tipo
		:class:`BrowsingContext<sdf.page_parser_driver.BrowsingContext>`
		"""
		if self.__navigate_func[0] == None:
			context.browser.load_page(self.__url)
		elif not self.__navigate_is_method :
			return self.__navigate_func[0](context)
		else:
			getattr(self.__parser_instance, self.__navigate_func[0])(context)
	