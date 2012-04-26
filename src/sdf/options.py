# *- encoding: utf-8 -*
import re
from sdf.util import Enum

Command = Enum('Run', 'Info')
ContinueOnItem = Enum(
					OnlyFinalize = -2, # solo finalize (válido para list based)
					ContinueLast = -1, 
					DoAllParsing = 0   
					) 

class Options(object):
	
	def __init__(self):
		self.command = Command.Run #IGNORE:E1101
		self.parser = None
		self.input_file = None
		self._output_file = None
		self.__continue_on_item = ContinueOnItem.DoAllParsing
		self.countries_file = None
		self.proxy_file = None
		self.default_encoding = "auto"
		
		# opciones del webkitBrowser
		self.use_webkitbrowser = False
		self.webkitbrowser_show = True
		self.webkitbrowser_showimages = True
		self.webkitbrowser_remain_open = False				
		
		# opciones para el retries del browser.load_page
		self.max_retries_load_page = 3
		
		# opciones para el max_time del browser.load_page (en segundos?)
		self.max_time_load_page = None
		
		# opciones de ListBasedParser
		self.list_based_parser_die_on_first_error = False
		
		# que clase de dataAdapter se usa
		import sdf
		self.data_adapter_class = sdf.DataAdapter
	
	@property
	def continue_last(self):
		return self.__continue_on_item == ContinueOnItem.ContinueLast
	
	@continue_last.setter
	def continue_last(self, value):
		if value:
			self.__continue_on_item = ContinueOnItem.ContinueLast
		else:
			self.__continue_on_item = ContinueOnItem.DoAllParsing
	
	@property
	def continue_on_item(self):
		return self.__continue_on_item
	
	@continue_on_item.setter
	def continue_on_item(self, value):
		self.__continue_on_item = value
	
	@property
	def only_finalize(self):
		return self.__continue_on_item == ContinueOnItem.OnlyFinalize
	
	@only_finalize.setter
	def only_finalize(self, value):
		if value:
			self.__continue_on_item = ContinueOnItem.OnlyFinalize
		else:
			self.__continue_on_item = ContinueOnItem.DoAllParsing
	
	
	@property
	def output_file(self):
		"Devuelve el valor de output_file"
		if self._output_file == None:
			return self.get_output_file()
		else:
			return self._output_file
			
	@output_file.setter
	def output_file(self, value):
		self._output_file = value
		
	@property
	def item_manager_database_file(self):
		"""
		Devuelve la ruta de la base de datos usada por el ItemManager para
		serializar los datos y para la recuperación
		"""
		return re.sub('(\..*)$', '', self.output_file) + "-recovery.db"  		
	
	def get_output_file(self):
		"""
		Devuelve el valor de output_file, si no está definido, puede ser
		sobrecargado por subclases para poner nombres como la gente
		"""
		if self.parser == None: # es raro que pase esto
			return "???.db"
		else: # devuelve el nombre del módulo del parser
			parts = self.parser.split('.') 
			if len(parts) >= 2:
				return parts[-2] + '.db'
			else:
				return self.parser + '.db'
