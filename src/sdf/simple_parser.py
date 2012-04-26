# *- encoding: utf-8 -*
from sdf.browsers import BrowserFactory
from sdf.helpers import StringHelper, DateHelper
from sdf import BaseParser

class SimpleParser(BaseParser):
	
	def __init__(self, context):
		BaseParser.__init__(self, context)
		self.__browser = None
		self.__context = context
	
	
	######### Propiedades ############
	
	@property
	def context(self):
		"""
		Devuelve el objeto del tipo :class:`Context` que tiene toda la información
		sobre el contexto de la ejecución
		"""
		return self.__context
	
	@property
	def state(self):
		"""
		Devuelve un objeto state donde se puede guardar información. Su uso
		está obsoleto pero se mantiene por compatibilidad hacia atrás
		"""
		return self.context.state
	
	@property
	def options(self):
		"""
		Devuelve las opciones de la corrida.
		Es un sinónimo de ``self.context.options``
		"""
		return self.context.options
	
	@property
	def data_adapter(self):
		"""
		Devuelve el objeto DataAdapter para almacenar los resultados de la
		parser.
		Es un sinónimo de ``self.context.data_adapter``
		"""
		return self.context.data_adapter
		
	@property
	def url_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.UrlHelper` asociado al
		parser.	Es un sinónimo de ``self.context.url_helper``
		"""
		return self.context.url_helper
	
	@property
	def email_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.EmailHelper` asociado al
		parser.	Es un sinónimo de ``self.context.email_helper``
		"""
		return self.context.email_helper
	
	@property
	def phone_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.PhoneHelper` asociado al
		parser.	Es un sinónimo de ``self.context.phone_helper``
		"""
		return self.context.phone_helper
	
	@property
	def text_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.TextHelper` asociado al
		parser.	Es un sinónimo de ``self.context.text_helper``
		"""
		return self.context.text_helper
	
	@property
	def string_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.StringHelper` asociado al
		parser.	Es un sinónimo de ``self.context.string_helper``
		"""
		return StringHelper
	
	@property
	def date_helper(self):
		"""
		Devuelve un :class:`sdf.helpers.DateHelper` asociado al
		parser.	Es un sinónimo de ``self.context.date_helper``
		"""
		return DateHelper
	
	@property
	def browser(self):
		"""
		Devuelve una instancia de 
		:class:`sdf.browsers.browser.Browser` asociado para usar en
		la navegación.
		
		Este browser puede ser un WebkitBrowser si se definió en las opciones
		el parámetro ``-W`` o un BasicBrowser de lo contrario.
		"""
		factory = BrowserFactory.get_instance()
		if self.__browser == None:
			if self.options.use_webkitbrowser:
				self.__browser = factory.get_webkitbrowser(
					self.options.webkitbrowser_show,
					self.options.webkitbrowser_showimages)
			else:
				self.__browser = factory.get_basicbrowser()
				
		return self.__browser
	
	################
	
	def _run(self):
		self.parse()

		# hace que no se cierre la ventana del browser
		if self.options.use_webkitbrowser and self.options.webkitbrowser_remain_open:
			return 1
	
	############## Métodos redefinibles ###########################
	def parse(self):
		"""
		Todo el código del parser se tiene que encontrar en esta método.
		Este método se llama por SDF al empezar el parseo.
		"""
		raise NotImplemented('Must be implemented in order to parse')


