# *- encoding: utf-8 -*
from sdf import Options, Context, properties
from sdf.browsers import bootstrap, BrowserFactory
from sys import argv, stderr
from os.path import join
from optparse import OptionParser
from sdf.util.typecheck import check_if_any_type
from sdf.parser_loader import ParserLoader
from types import NoneType
from sdf.browsers.bootstrap import BootstrapEventHandler, BootStrap

class Driver(object):
	"""
	Clase que modela la ejecución del parser. Puede ser derivada en los parsers
	para definir opciones especiales que tome el programa.
	"""
	
	def __init__(self):
		self.__options = None
		self.__parser = OptionParser(version=self.get_version())
		self.__parser_loader = _DefaultParserLoader()
		
	
	########### Métodos redefinibles ##################
	def get_version(self):
		"""Retorna la versión del programa. Por defecto retorna la versión de 
		SDF"""
		return "SDF v%s" % properties.Properties.version
	
	def get_program_name(self):
		"Retorna el nombre del programa"
		return argv[0]
	
	def handle_options(self, parsed_options, options):
		"""
		Llamado para manejar las opciones, el argumento parsed_options tiene las
		opciones parseadas
		
		parsed_options
			Las opciones parseadas
		options
			El objeto options donde se ponen las opciones
		"""
		pass
		
	
	###################################################


	def add_option(self, short_name, long_name, dest, help_string = None,
				   metavar = None):
		"Agrega una opción al parser"
		self.__parser.add_option(short_name, long_name, dest = dest,
								 help = help_string, metavar = metavar)
	
	def execute(self,
			args=None,
			options = None,
			context = None,
			bootstrap_event_handler = None):
		"Hace la ejecución de un parser según las opciones que se pasaron"
		if options == None:
			options = Options()
		if context == None:
			context = Context(options)
		
		check_if_any_type(bootstrap_event_handler, [NoneType, BootstrapEventHandler])
		check_if_any_type(options, Options)
		check_if_any_type(context, Context)

		self.__run(context, options, args, bootstrap_event_handler)
	
	@property
	def parser_loader(self):
		"""
		Tiene la clase derivada de ParserLoader que se encarga de cargar el
		módulo
		"""
		return self.__parser_loader
	
	@parser_loader.setter
	def parser_loader(self, value):
		self.__parser_loader = value
		
	####################################################
	
	def __get_options(self, options, args=None):
		parser = self.__parser
		
		usage = """%s [Options]""" % self.get_program_name()
		parser.set_usage(usage)
		parser.add_option("-p", "--parser", dest="parser",
						  help="Indica el nombre parser en <name>",
						  metavar="<name>")
		parser.add_option("-o", "--output-file", dest="output_file",
						  help="Indica el archivo de salida en <file>",
						  metavar="<file>")
		parser.add_option("-i", "--input-file", dest="input_file",
						  help="Indica el archivo de entrada en <file>",
						  metavar="<file>")
		parser.add_option("-c", "--continue-last",
						  action="store_true", dest="continue_last",
						  help="""
						  Continua la última corrida (válido solo para
						  UrlBasedParser y ListBasedParser""")
		parser.add_option("-u", "--countries-file", dest="countries_file",
						  help="indica el archivo de paises <file>",
						  metavar="<file>")
		
		######### Opciones del browser ###########
		parser.add_option("-W", "--use-webkitbrowser", dest="use_webkitbrowser",
						  help="Habilita el uso de webkitbrowser",
						  action="store_true")
		parser.add_option("--wk-hide-browser", dest="hide_browser",
						  help="Hace que webkitbrowser oculte la ventana principal",
						  action="store_true")
		parser.add_option("--wk-hide-images", dest="hide_images",
						  help="Oculta las imágenes en webkitbrowser",
						  action="store_true")
		parser.add_option("--proxy", dest="proxy_file",
						  help="indica el archivo de proxies <file>",
						  metavar="<file>")
		parser.add_option("--retries", dest="max_retries",
						  help="indica la cantidad máxima de retries por carga de página en <r>",
						  metavar="r")
		#agrega la opción para max_time
		parser.add_option("-M", "--max_time", dest="max_time",
						  help="indica el tiempo máximo a esperar a cargar la página <r>",
						  metavar="r")
		parser.add_option("-e", dest="default_encoding",
						  help="indica la codificacion por defecto en el browser"
						  )
		
		help = "Impide que se cierra la ventana del browser luego de finalizar " 
		help += "el parseo"
		parser.add_option("--wk-remain-open", dest="remain_open",
						  help= help,
						  action="store_true")
		
		######### Opciones del ListBasedParser ###########
		help =  "Hace que el parser termine en el primer error en el "
		help += "procesamiento de items (Solo ListBasedParser)"
		parser.add_option("-d", "--die-on-first", dest="lsb_die_on_first",
						  help=help, action="store_true")
		
		help  = "Hace que el list based parser vuelva a arrancar desde el item "
		help += "<item> a pesar de que se hayan procesado. Por ejemplo si se "
		help += "pone el valor 1 omite el paginado y empieza el procesamiento "
		help += "de nuevo"
		parser.add_option("-n", "--continue-on-item", dest="continue_on_item",
						help=help, metavar="<item>")
		help = "Hace que el list based parser haga solo el finalize"
		parser.add_option("-f", "--only-finalize",
						dest="only_finalize", action='store_true',
						help=help)
			
		# parsea los argumentos
		if args == None:
			(o, a) = parser.parse_args()
		elif isinstance(args, list):
			(o, a) = parser.parse_args(args)
		elif isinstance(args, str) or isinstance(args, str):
			(o, a)= parser.parse_args(args.split(' ')) 
		else:
			raise TypeError("list, str or unicode expected, but %s given" % \
				args.__class__.__name__)
		
		# llena el objeto options
		if len(a) != 0:
			raise NameError('Too many commands: ' + ' '.join(a))
		if o.parser != None:
			options.parser = o.parser
		if o.output_file != None:
			options.output_file = o.output_file
		if o.continue_last != None:
			options.continue_last = o.continue_last
		if o.countries_file != None:
			options.countries_file = o.countries_file
		if o.use_webkitbrowser != None:
			options.use_webkitbrowser = o.use_webkitbrowser
		if o.hide_browser != None:
			options.webkitbrowser_show = not o.hide_browser
		if o.hide_images != None:
			options.webkitbrowser_showimages = not o.hide_images
		if o.remain_open != None:
			options.webkitbrowser_remain_open = o.remain_open
		if o.lsb_die_on_first != None:
			options.list_based_parser_die_on_first_error = o.lsb_die_on_first
		if o.continue_on_item != None:
			options.continue_on_item = int(o.continue_on_item)
		if o.only_finalize != None:
			options.only_finalize = o.only_finalize
		if o.proxy_file != None:
			options.proxy_file = o.proxy_file
		if o.max_retries != None:
			options.max_retries_load_page = int(o.max_retries)
		if o.max_time != None:
			options.max_time_load_page = int(o.max_time)	
		if o.default_encoding != None:
			options.default_encoding = o.default_encoding
			
		self.handle_options(o, options)

			
	def __run(self, context, options, args, bootstrap_event_handler):
		try:
			self.__get_options(options, args)
		except NameError as ex:
			print("Error while parsing command line arguments: %s" % ex, file=stderr)
			self.__parser.print_help()
			exit(1)
		
		if not options.countries_file:
			cf = join('config', 'countries.info')
			options.countries_file = cf
		
		if not options.output_file:
			options.output_file = None
		
		# importa el parser
		try:
			parser_class = self.__parser_loader.get_parser_class(options)
		except ImportError as ex:
			print("Error while loading Parser module %s: %s" % (
				str(options.parser), ex), file=stderr) 
			exit(1)
		
			
		from sdf import BaseParser
		if not issubclass(parser_class, BaseParser):
			print("%s must be a Parser class" % options.parser, file=stderr)
			exit(1) 
		
		BrowserFactory.create_instance(context)
		parser = parser_class(context)
		context._set_parser(parser)
		self.__parser_loader.parser_loaded(context, parser)
		BootStrap.init_and_work(parser.run, bootstrap_event_handler)

class _DefaultParserLoader(ParserLoader):
	"""Un cargador de parser que usa los argumentos que se pasaron"""
	def get_parser_class(self, options):
		"parsea la opción del parser y lo importa"
		if not options.parser:
			raise ImportError('-p <name> not supplied')
		
		parser_parts = options.parser.split('.')
		if len(parser_parts) > 1:
			parser_class = options.parser.split('.')[-1]
			parser_module = '.'.join(options.parser.split('.')[0:-1])
		else:
			parser_class = options.parser.split('.')[0]
			parser_module = "__main__"
		
		parser_module = __import__(parser_module, globals(), locals(),
								   [parser_class], -1)
		
		try:
			parser_class = parser_module.__getattribute__(parser_class)
		except AttributeError:
			msg = "%s has no member named %s" % (parser_module,	parser_class)
			raise ImportError(msg)
		
		return parser_class	