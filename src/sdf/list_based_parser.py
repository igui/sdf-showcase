# *- encoding: utf-8 -*
'''
Created on 11/03/2010

@author: iavas
'''

from sdf.util import synchronized_method, eta
from sdf import LogicError, BaseParser
from sdf.options import ContinueOnItem
from sdf.browsers import BrowserFactory
from sdf.util import check_if_any_type, Enum
from sdf.data import Item
import sdf.browsers
from sdf.helpers import StringHelper
from threading import Lock
from time import time
import traceback
import sys
from sdf import ItemProcesorPipeline
from sdf import ItemManager
from sdf.exception import LoadPageError
import datetime


class ListBasedParser(BaseParser):
	"Un parser basado en una lista de items"
	
	browser_type = BrowserFactory.browser_type
	"""
	Enumerado para indicar el tipo de browser, toma los valores
	
	* *BasicBrowser* para BasicBrowser
	* *WebKitBrowser* para WebKitBrowser
	* *DefaultBrowser* para denotar al browser usado por defecto
	"""
	
	def __init__(self, context):
		BaseParser.__init__(self, context)
		
		check_if_any_type(context, sdf.Context)
		self.__context = context
		self.__item_manager = None
		self.__pipeline = None
		self.__browser_pool = None
		
	def _run(self):
		"""
		Hace el parseo, no se debe redefinir en las clases que derivan del
		parser
		"""
		#self.log(str(self.__context.options.continue_on_item))
		continue_on = self.__context.options.continue_on_item
		
		if continue_on == ContinueOnItem.OnlyFinalize:
			# solo finalize
			self.__do_only_finalize()
			return
		
		elif continue_on == ContinueOnItem.DoAllParsing:
			# hace todo: paginado + procesamiento + finalize
			im_db_file = self.__context.options.item_manager_database_file
			self.__item_manager = ItemManager(im_db_file, replace_items = True) 
			self.__make_paging_call_sequence()
			to_process = self.__item_manager.unprocessed_items
			
		elif continue_on == ContinueOnItem.ContinueLast:
			# no hace el paginado, agarra los items sin procesar
			im_db_file = self.__context.options.item_manager_database_file 
			self.__item_manager = ItemManager(im_db_file, replace_items = False)
			to_process = self.__item_manager.unprocessed_items
			self.log("Continuando corrida, quedan por procesar %d items" % \
				len(to_process))
		
		else:
			# empieza incondicionalmente desde un cierto item
			im_db_file = self.__context.options.item_manager_database_file 
			self.__item_manager = ItemManager(im_db_file, replace_items = False)
			
			self.__item_manager.set_processed_from(continue_on, False)
			to_process = self.__item_manager.unprocessed_items
			
			self.log("Continuando corrida, quedan por procesar %d items" % \
				len(to_process))
		
		self.__process_items(to_process)
		self.__finalize_call_sequence()
	
	def __process_items(self, to_process):
		"Procesa los items"
		self.log("Comenzando procesado. Usando %d browsers" % 
				self.get_paralel_num())
				
		# crea el pool de browsers
		self.__browser_pool = _BrowserPool()
		for _ in range(self.get_paralel_num()):
			self.__browser_pool.add_browser(self.__get_browser(
										self.get_process_item_browser_type()
										)
			)
		
		# pone a procesar todos los items
		progress = eta.Progress(len(to_process), unit = "pag")
		pipeline = ItemProcesorPipeline(self.get_paralel_num())
		
		start = time()
		
		# convierte los items a una lista para tenerlos todos antes de
		# agregarlos al pipeline
		to_process = list(to_process)
		for item_manager_item in to_process:
			# print "pusheando %d" % item_manager_item.item_num
			pipeline.push(self.__process_item_call_sequence,
						item_manager_item,
						len(to_process),
						progress,
						pipeline
				)
		
		pipeline.wait_end() # espera a que termine de procesar
		
		processing_time_str =  eta.time_string(time() - start)
		self.log("Procesamiento terminado en %s" % processing_time_str)
		
	
	def __do_only_finalize(self):
		"solo hace el finalize"
		im_db_file = self.__context.options.item_manager_database_file
		self.__item_manager = ItemManager(im_db_file, replace_items = False)
		self.log("Continuando corrida con finalize")
		self.__finalize_call_sequence()
		
	def __get_browser(self, browser_type):
		"Obtiene un browser según una clase dada"
		if browser_type == self.browser_type.BasicBrowser:
			return BrowserFactory.get_instance().get_basicbrowser()
		
		elif browser_type == self.browser_type.WebKitBrowser:
			show_images = self.__context.options.webkitbrowser_showimages
			show = self.__context.options.webkitbrowser_show
			return BrowserFactory.get_instance().get_webkitbrowser(show,
																show_images)
		
		elif browser_type == self.browser_type.DefaultBrowser:
			if self.__context.options.use_webkitbrowser:
				return self.__get_browser(self.browser_type.WebKitBrowser)
			else:
				return self.__get_browser(self.browser_type.BasicBrowser)
					
		else:
			raise LogicError("Unknown browser type")
	
	def __make_paging_call_sequence(self):
		"hace el paginado y chequea la respuesta"

		self.log("Comenzado paginado")

		start = time()
		
		browser = self.__get_browser(self.get_paging_browser_type())
		paging_res = self.make_paging(MakePagingContext(self.__context,browser))
		
		# chequea el tipo de los elementos retornados
		if not hasattr(paging_res, '__iter__'):
			raise TypeError("make_paging() returned %s, but it must return a" +\
				" list" % type(paging_res).__name__)
		
		# chequea uno a uno los elementos retornados		
		for paged_item in paging_res:
			if not isinstance(paged_item, Item):
				raise TypeError("make_paging must return a list of Item " +\
					"objects, but it returned an item of type %s" % (
						type(paged_item).__name__))
		
		paging_time = time() - start
	
		self.log("Fin paginado, en %s . Obtenidos %s items" % 
				(eta.time_string(paging_time),  len(paging_res)) )
		
		# agrega los items
		self.__item_manager.add(paging_res)
				
		return paging_res
		
	def __process_item_call_sequence(self,
									item_manager_item,
									total_items,
									eta_obj,
									pipeline):
		"Llamada al procesar el item"
		#print "procesando %d" %  item_manager_item.item_num
		
		start_time = time()
		
		# print "pool %d" %  item_manager_item.item_num 
		browser = self.__browser_pool.get_browser()
		# print "pool_done %d" %  item_manager_item.item_num
		
		try:
			processed_ok = False
			
			# carga la url del item a parsear
			try:
				browser.load_page(item_manager_item.stored_item.url)
			except:
				raise LoadPageError("Error al cargar la página %s" % \
					item_manager_item.stored_item.url)
					
			self.process_item (
				ProcessItemContext(self.__context, browser),
				item_manager_item.stored_item
			)
			
			processed_ok = True			
			item_manager_item.store_item()
			
			#print "semi processed %d" %  item_manager_item.item_num
		except:
			e_str = self.__handle_last_error("Error procesando item %d" % 
									(item_manager_item.item_num + 1))
			self.__item_manager.add_error(item_manager_item.item_num, e_str)
			
			# cancela el procesamiento en el primer error
			if self.__context.options.list_based_parser_die_on_first_error:
				pipeline.cancel_queue()		

		self.__browser_pool.free_browser(browser)
		
		if processed_ok:
			item_manager_item.processed = True
			processed_res_str = "OK"
		else:
			processed_res_str = "ERROR"
			
		process_time = time() - start_time
		eta_obj.increment()
				
		self.log(
			"Procesado item %d (%s) [%d/%d] en %.2fs Vel: %s ETA: %s" %
			(item_manager_item.item_num, processed_res_str,
			eta_obj.history[-1][0], total_items, process_time,
			eta_obj.overall_rate_str(), eta_obj.time_remaining_str())
		)
		
	def __finalize_call_sequence(self):
		"Hace todo lo necesario para la llamada a finalize, si corresponde"
		starttime = time()
		processed_items = self.__item_manager.stored_processed_items
		unprocessed_items = self.__item_manager.stored_unprocessed_items
		
		
		msg  = "Comenzando finalización. Procesados %d items, "
		msg += "no procesados %d items"
		self.log(msg % (len(processed_items), len(unprocessed_items)))
		
		try:
			self.finalize(FinalizeContext(self.__context),
						processed_items,
						unprocessed_items)
		except:
			e_str = self.__handle_last_error("Error en llamada a finalize()")
			self.__item_manager.add_error(-1, e_str)
			
		ellapsed = eta.time_string(time() - starttime) 
		self.log("Finalización completada en %s" % ellapsed)
		
	def __handle_last_error(self, pre_string = None):
		"""
		Función para loggear un error correctamente, pone una línea con la
		descripción del error, se usa pre_string ahi. Se imprime el error en el
		log y se devuelve la cadena del error impresa 
		"""
		
		if pre_string == None:
			pre_string = "Error"
		
		error_type, error_value, trbk = sys.exc_info()
		tb_list = traceback.format_tb(trbk)    
		error_str = "%s: %s: %s\n" % (
				pre_string,
				error_type.__name__, error_value)
		if len(tb_list) > 1:
			error_str += "Traceback:"
			for i in tb_list[1:]: # se ignora la 1ra llamada (esta función)
				error_str += "\n" + i
		self.log(error_str + "\n")
		return error_str

	######################## Funciones redefinibles ##########################
	
	def get_paralel_num(self):
		"""
		Define la cantidad de items que se procesan en paralelo.
		Por defecto es 2
		"""
		return 2
	
	def get_paging_browser_type(self):
		"""
		Devuelve la clase de browser que se usa para hacer el paginado.
		Los valores que se aceptan son 
		
		* ListBasedBrowser.browser_type.BasicBrowser para usar BasicBrowser  
		* ListBasedBrowser.browser_type.WebKitBrowser para usar WebKitBrowser
		* ListBasedBrowser.browser_type.DefaultBrowser para usar el browser por
			defecto (se usa WebkitBrowser si se define ``-W`` en las opciones).
			Esta es la opción usada por defecto
		""" 
		return self.browser_type.DefaultBrowser
	
	def get_process_item_browser_type(self):
		"""
		Igual que :func:`get_paging_browser_type` pero para definir el browser
		que se usa al procesar items
		"""
		return self.browser_type.DefaultBrowser
	
	def make_paging(self, context):
		"Hace el paginado"
		raise NotImplementedError
	
	def process_item(self, context, item):
		"Procesa un item."
		raise NotImplementedError
	
	def finalize(self, context, processed_items, unprocessed_items):
		"Se llama luego de procesar los items"
		pass

class ListBasedParserContextBase(object):
	"La clase base para los Contextos en ListBasedParser"
	
	def __init__(self, context):
		"Constructor, necesita un sdf.Context"
		check_if_any_type(context, sdf.Context)
		self.__context = context
		
	@property
	def text_helper(self):
		return self.__context.text_helper
	
	@property
	def email_helper(self):
		return self.__context.email_helper
	
	@property
	def phone_helper(self):
		return self.__context.phone_helper
	
	@property
	def string_helper(self):
		return StringHelper
	
	@property
	def url_helper(self):
		return self.__context.url_helper
	
	@property
	def proxies(self):
		return self.__context.proxies
	
	@property
	def postactions(self):
		return self.__context.postactions
	
	@property
	def options(self):
		return self.__context.options

class FinalizeContext(ListBasedParserContextBase):
	"El contexto que se usa en finalize()"
	def __init__(self, context):
		ListBasedParserContextBase.__init__(self, context)
		self.__context = context
		
	@property
	def data_adapter(self):
		return self.__context.data_adapter
	

class MakePagingContext(ListBasedParserContextBase):
	"""
	El contexto que se pasa a la función make_paging(), tiene las variables que
	se pueden usar allí
	"""
	def __init__(self, context, browser):
		check_if_any_type(browser, sdf.browsers.Browser)
		
		ListBasedParserContextBase.__init__(self, context)
		self.__browser = browser
	
	@property
	def browser(self):
		"Un browser para hacer el paginado" 
		return self.__browser
	
	
class ProcessItemContext(MakePagingContext):
	"""
	El contexto que se pasa a la función process_item(), tiene las variables que
	se pueden usar allí
	"""
	def __init__(self, context, browser):
		check_if_any_type(browser, sdf.browsers.Browser)
		
		MakePagingContext.__init__(self, context, browser)
	
	@property
	def data_adapter(self):
		return self.__context.data_adapter


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
		