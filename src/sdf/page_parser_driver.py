# *- encoding: utf-8 -*
'''
Created on 28/07/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
from sdf.browsers.browser import Browser
from sdf.context import Context
from sdf.page_manager import PageHandler, DefaultPageManager,\
	AddPageListener
from sdf.helpers.string_helper import StringHelper
from sdf.util import eta
from sdf import ItemProcesorPipeline
import traceback
from time import time
import sys
from sdf.page_parser import Page
from sdf.util.eta import Progress


class BasePageParserDriver(object):
	'''
	Maneja la ejecución de un PageParser pero es abstracta y es un template
	method
	'''
	
	def __init__(self, context, parser):
		from .page_parser import PageParser
		check_if_any_type(parser, PageParser)
		self.__parser = parser
		self.__context = context
		
		self.log = self.__parser.log
		self.get_paralel_num = self.__parser.get_paralel_num
		
		self.__page_manager = None

	@property
	def page_manager(self):
		"""
		Retorna el page_manager o None si todavía no se está corriendo el parser
		"""
		return self.__page_manager
	

	######### Métodos redefinibles
	
	def on_process_page(self, pending_page):
		"Se llama cuando hay que procesar una página"
		raise NotImplementedError
	
	def on_finalize(self, processed, unprocessed):
		"Se llama cuando se tiene que hacer en el finalize"
		raise NotImplementedError
	
	def run(self):
		"Corre el parser según las opciones"
		db_file = self.__context.options.item_manager_database_file
		
		if self.__context.options.only_finalize:
			# solo finalize
			page_manager = DefaultPageManager(db_file, None, self.__parser)
			self.__page_manager = page_manager
			self.log("Continuando corrida solo con finalize")
			self.__finalize_call_sequence(page_manager)

		else:
			# corrida normal
			if not self.__context.options.continue_last:
				start_func = self.__parser.start
			else:
				start_func = None
			page_manager = DefaultPageManager(db_file,start_func, self.__parser)
			self.__page_manager = page_manager
			self.__process_pages(page_manager)
			self.__finalize_call_sequence(page_manager)
		
	def __process_pages(self, page_manager):
		"Procesa las páginas"
		
		paralel_num = self.get_paralel_num()
		if paralel_num == 1:
			self.log("Comenzando procesado. Usando un browser")
		else:
			self.log("Comenzando procesado. Usando %d browsers" % paralel_num)
				
		pipeline = ItemProcesorPipeline(paralel_num)
		start = time()
		
		progress = Progress(0, "pagina")
		
		page_manager.on_add_page_suscribe(_AddPageListener(
											pipeline,
											self.__process_page_call_sequence,
											progress
										  )
										)
		
		while True:
			pending_page = page_manager.get_pending_page()
			if pending_page == None:
				break
			
			pipeline.push(
				self.__process_page_call_sequence,
				page_manager,
				pending_page,
				pipeline,
				progress
			)
				
		pipeline.wait_end() # espera a que termine de procesar
		
		processing_time_str =  eta.time_string(time() - start)
		self.log("Procesamiento terminado en %s" % processing_time_str)
		
	def __process_page_call_sequence(self,
									page_manager,
									pending_page,
									pipeline,
									progress):
		"Llamada al procesar una página"
		start_time = time()
		
		try:
			processed_ok = False
			
			self.on_process_page(pending_page)
			
			processed_ok = True
		except:
			e_str = self.__handle_last_error("Error procesando pagina %d" % 
									(pending_page.id))
			page_manager.add_error(pending_page.id, e_str)
			
			# cancela el procesamiento en el primer error
			if pending_page.page.end_on_error:
				pipeline.cancel_queue()
		
		if processed_ok:
			pending_page.state = PageHandler.PageState.Finished
			processed_res_str = "OK"
		else:
			pending_page.state = PageHandler.PageState.Failed
			processed_res_str = "ERROR"
			
		process_time = time() - start_time
		
		finished, total = page_manager.count_pages()
		progress.increment()
				
		self.log(
			"Procesada pag. %d (%s) [%d/%d] en %.2fs (%s)." %
			(pending_page.id, processed_res_str, finished, total, process_time,
			progress.overall_rate_str())
		)

		

	def __finalize_call_sequence(self, page_manager):
		"Llama a finalize y amigos"
		
		processed = page_manager.get_processed_items()
		unprocessed = page_manager.get_unprocessed_items()
		
		starttime = time()
		
		msg  = "Comenzando finalizacion. Procesados %d items, "
		msg += "no procesados %d items"
		self.log(msg % (len(processed), len(unprocessed)))
		
		try:
			self.on_finalize(processed, unprocessed)
		except:
			e_str = self.__handle_last_error("Error en llamada a finalize()")
			page_manager.add_error(-1, e_str)
			
		ellapsed = eta.time_string(time() - starttime) 
		self.log("Finalizacion completada en %s" % ellapsed)

	
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

class _AddPageListener(AddPageListener):
	"Listener para agregar una página"
	
	def __init__(self, pipeline, callback_func, progress):
		AddPageListener.__init__(self)
		self.__pipeline = pipeline
		self.__callback_func = callback_func
		self.__progress = progress
		
		
	def on_add_page(self, page_manager, page_handler):
		pending_page = page_manager.get_pending_page()
		if pending_page == None:
			return
		self.__pipeline.push(self.__callback_func,
			page_manager,
			pending_page,
			self.__pipeline,
			self.__progress
		)
		


class PageParserContextBase(object):
	"La clase base para los Contextos en PageParserContext"
	
	def __init__(self, context):
		"Constructor, necesita un sdf.Context"
		check_if_any_type(context, Context)
		self.__context = context
	
	@property
	def data_adapter(self):
		"El DataAdapter usado para guardar datos"
		return self.__context.data_adapter
	
	@property
	def text_helper(self):
		"""
		Atajo para :class:`TextHelper <sdf.helpers.TextHelper>` 
		"""
		return self.__context.text_helper
	
	@property
	def email_helper(self):
		"""
		Atajo para :class:`EmailHelper <sdf.helpers.EmailHelper>` 
		"""
		return self.__context.email_helper
	
	@property
	def phone_helper(self):
		"""
		Atajo para :class:`PhoneHelper <sdf.helpers.PhoneHelper>` 
		"""
		return self.__context.phone_helper
	
	@property
	def string_helper(self):
		"""
		Atajo para :class:`StringHelper <sdf.helpers.StringHelper>` 
		"""
		return StringHelper
	
	@property
	def url_helper(self):
		"""
		Atajo para :class:`UrlHelper <sdf.helpers.UrlHelper>` 
		"""
		return self.__context.url_helper
	
	@property
	def options(self):
		"""
		Atajo para :class:`UrlHelper <sdf.helpers.UrlHelper>` 
		"""
		return self.__context.options


class BrowsingContext(PageParserContextBase):
	"""
	Un contexto para navegar en las páginas
	"""
	
	def __init__(self, context, browser):
		PageParserContextBase.__init__(self, context)
		check_if_any_type(browser, Browser)
		self.__browser = browser
	
	@property
	def browser(self):
		"La instancia de browser para navegar"
		return self.__browser


class PagingContext(BrowsingContext):
	"El contexto que se usa para paginar" 
	
	def __init__(self, browser, context, current_page_handler):
		BrowsingContext.__init__(self, context, browser)
		check_if_any_type(current_page_handler, PageHandler)
		self.__current_page_handler = current_page_handler
	
	def add_page(self, page_or_url, *args, **kwargs):
		"""
		Agrega una página como hija de la página actual. 
		Esa página se va a procesar luego de procesar la página actual.
			
		El primer argumento puede ser tanto un objeto
		:class:`Page<sdf.page_parser.Page>` como una url. Si es una
		url internamente se convierte a una página y se usan los argumentos
		en args y kwargs para inicializar al constructor de la página.
		Por esto las siguientes llamadas son equivalentes: ::
		
			context.add_page(
			    'http://www.metacafe.com/videos/art_and_animation/week',
			    parse = self.parse_page
			)
			
			context.add_page(
			    Page(
			         'http://www.metacafe.com/videos/art_and_animation/week',
			         parse = self.parse_page
			    )
			)
			
			
		"""
		
		if isinstance(page_or_url, str):
			page_or_url = Page(page_or_url, *args, **kwargs)
		
		self.__current_page_handler.add_page(page_or_url)
		
	def add_item(self, item):
		"Agrega un objeto item procesado a la página actual"
		self.__current_page_handler.add_item(item)
		
	@property
	def page(self):
		"La página actual que se está parseando"
		page_handler = self.__current_page_handler
		page = page_handler.page
		return page

