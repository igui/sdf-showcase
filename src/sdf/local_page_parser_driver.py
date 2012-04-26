# *- encoding: utf-8 -*
'''
Created on 24/08/2010

@author: iavas
'''
from .page_parser_driver import BasePageParserDriver, BrowsingContext
from .exception import LoadPageError, LogicError
from .page_parser_driver import PagingContext
from sdf.browsers.browserfactory import BrowserFactory
from threading import Lock
from sdf.util.synchronized import synchronized_method


class LocalPageParserDriver(BasePageParserDriver):
	"""
	Modela un driver de procesa las páginas localmente en la máquina
	"""
	
	def __init__(self, context, parser):
		BasePageParserDriver.__init__(self, context, parser)
				
		self.__context = context
		self.__parser = parser

		# crea el pool de browsers
		self.__browser_pool = _BrowserPool()
		for _ in range(self.__parser.get_paralel_num()):
			self.__browser_pool.add_browser(self.__get_browser())
			
			
	def on_process_page(self, pending_page):
		"""
		Se llama cuando hay que procesar una página y se retorna cuando se
		terminó de procesar la página
		"""
		try:
			browser = self.__browser_pool.get_browser()
			
			# carga la url del item a parsear
			try:
				context = PagingContext(browser, self.__context, pending_page)
				pending_page.page.navigate(context)
			except Exception as ex:
				e_str = "Error al navegar a la página %s: %s" %	(
						pending_page.page.url, ex)
				raise LoadPageError(e_str)
				
			
			
			pending_page.page.parse(context)
		finally:
			self.__browser_pool.free_browser(browser)
		
	
	def on_finalize(self, processed, unprocessed):
		browser = self.__browser_pool.get_browser()
		context = BrowsingContext(self.__context, browser)
		self.__parser.finalize(context, processed, unprocessed)
	
	def __get_browser(self):
		"Obtiene un browser según una clase dada"
		if not self.__context.options.use_webkitbrowser:
			return BrowserFactory.get_instance().get_basicbrowser()
		else:
			show_images = self.__context.options.webkitbrowser_showimages
			show = self.__context.options.webkitbrowser_show
			return BrowserFactory.get_instance().get_webkitbrowser(
																show,
																show_images
																)

class _BrowserPool(object):
	"Una piscina de browsers para reusar"

	def __init__(self):
		self.lock = Lock()
		self.__browsers = set()
		self.__freed = set()
	
	@synchronized_method('lock')	
	def get_browser(self):
		"Obtiene un browser libre de la piscina"
		if len(self.__freed) == 0:
			raise LogicError("No browsers available")
		return self.__freed.pop()
	
	@synchronized_method('lock')
	def free_browser(self, browser):
		"Devuelve un browser a la piscina"
		if browser not in self.__browsers:
			raise ValueError("browser doesn't belong to the pool")
		if browser in self.__freed:
			raise LogicError("browser already freed")
		else:
			self.__freed.add(browser)
			
	@synchronized_method('lock')
	def add_browser(self, browser):
		"Agrega un browser a la piscina"
		if browser in self.__browsers:
			raise ValueError("browser already belong to the pool")
		
		self.__browsers.add(browser)
		self.__freed.add(browser)
		