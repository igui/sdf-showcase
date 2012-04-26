# *- encoding: utf-8 -*
from sdf.data import Countries
from sdf.helpers import TextHelper, EmailHelper, PhoneHelper, UrlHelper
from sdf import State, Logger
from sdf.item_manager import ItemManager
from sdf.postactions import PostActionManager
from sdf.util.typecheck import check_if_any_type
from sdf.logger import RedirectLogger, MainLogger
from os import path
import sys

class Context(object):
	"""
	Representa el contexto de ejecución de un parser y todas las variables
	asociadas. 
	"""
	
	def __init__(self, options):
		self.__countries = None
		self.__options = options
		self.__state = State()
		self.__data_adapter = None
		self.__item_manager = None 
		self.__text_helper = TextHelper(self)
		self.__email_helper = EmailHelper(self)
		self.__phone_helper = PhoneHelper(self)
		self.__url_helper = UrlHelper(self)
		self.__logger = MainLogger()
		self.__proxies = None
		self.__postactions = PostActionManager(self)
		self.__parser = None
		
	@property
	def options(self):
		"Retorna el objeto :class:`Options` asociado al contexto"
		return self.__options
	
	@property
	def logger(self):
		"Devuelve un :class:`Logger` para loguear eventos"
		return self.__logger
	
	@property
	def state(self):
		"Da el objeto state del contexto, su uso es obsoleto"
		return self.__state

	@state.setter
	def state(self, value):
		self.__state = value
	
	@property
	def text_helper(self):
		"""
		Devuelve un :class:`TextHelper<sdf.helpers.TextHelper>`
		asociado al	contexto
		"""
		return self.__text_helper
	
	@property
	def email_helper(self):
		"""
		Devuelve un :class:`EmailHelper<sdf.helpers.EmailHelper>`
		asociado al contexto
		"""
		return self.__email_helper
	
	@property
	def phone_helper(self):
		"""
		Devuelve un :class:`PhoneHelper<sdf.helpers.PhoneHelper>`
		asociado al	contexto
		"""
		return self.__phone_helper
	
	@property
	def url_helper(self):
		"""
		Devuelve un :class:`UrlHelper<sdf.helpers.UrlHelper>`
		asociado al	contexto
		"""
		return self.__url_helper
	
	@property
	def data_adapter(self):
		"""
		Devuelve un :class:`DataAdapter` asociado al contexto
		"""
		if self.__data_adapter is None:
			self.__data_adapter = self.options.data_adapter_class(self)
		return self.__data_adapter
	
	@property
	def item_manager(self):
		if self.__item_manager is None:
			self.__item_manager = ItemManager(self)
		return self.__item_manager
	
	@property
	def countries(self):
		if self.__countries == None:
			self.__countries = Countries(self)
		return self.__countries	
	
	@property
	def proxies(self):
		"""
		El administrador de proxies
		(:class:`ProxyManager<sdf.browsers.ProxyManager>`)
		"""
		if self.__proxies == None:
			from sdf.browsers.proxy import ProxyManager
			self.__proxies = ProxyManager(self, self.__options.proxy_file)
		return self.__proxies	
	
	@property
	def postactions(self):
		"""
		El administrador de postactions
		:class:`PostActionManager<sdf.postactions.PostActionManager>`
		para manejar las postactions del parser
		"""
		return self.__postactions

	@property
	def parser(self):
		"""
		El parser que está ejecutando
		"""
		return self.__parser
	
	@property
	def parser_name(self):
		"Da el nombre del parser (el módulo que lo contiene)"
		if self.__parser == None:
			raise AttributeError("No parser setted")
		
		module = self.__parser.__class__.__module__
		
		if module == '__main__': # el parser se ejecuta desde el módulo pricipal
			script_filename = path.split(sys.argv[0])[-1]
			module = script_filename.split('.')[0]
		else:
			module = module.split('.')[-1]
		
		return module

	# setea el parser	
	def _set_parser(self, parser):
		from .base_parser import BaseParser
		check_if_any_type(parser, BaseParser)
		self.__parser = parser
		