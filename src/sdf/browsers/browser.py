# *- encoding: utf-8 -*
'''
Created on 20/08/2009

@author: iavas
'''
from time import sleep
from sdf.util.typecheck import check_if_any_type 
import threading
from .dom import DOM
import os.path
import os
from urllib.parse import urlparse
from .request import Request
from types import NoneType
from traceback import print_exc

class Browser(DOM):
	'''Interfaz para representar un browser'''
	
	def __init__(self, context):
		DOM.__init__(self)
		self.__encoding = context.options.default_encoding
		self.__context = context
		
	##### Métodos de DOM sin implementar
	def get_html(self):
		raise NotImplementedError
	
	def get_elements_by_xpath(self, xpath):
		raise NotImplementedError
	#####
		
	def _load_page(self, url):
		"""
		Carga la página web indicada por url.
		En caso de que la página no pueda ser cargada lanza un LoadPageError
		"""
		raise NotImplementedError
	
	def load_page(self,
				url_or_request,
				retries = None,
				sleep_time = 5,
				max_time = None):
		"""
		Carga una página
		
		*url_or_request*
			la url de la página o un objeto
			:class:`Request<sdf.browsers.request.Request>` con el
			request si no es un GET, por ejemplo si se necesita hacer un POST
		*retrys*
			la cantidad de reintentos para cargar la página (3 por defecto o
			lo que se defina en la opción --retrys del parser)
		*sleep_time*
			la cantidad de tiempo(en segundos) a dormir entre reintentos 
		*max_time*
			el tiempo máximo a esperar a cargar la página (Infinito por defecto) 
		"""
		check_if_any_type(url_or_request, [str, Request])
		check_if_any_type(retries, [int, int, NoneType])
		check_if_any_type(max_time, [int, int, NoneType])
		
		if retries == None:
			retries = self.__context.options.max_retries_load_page
		
			# es url, lo transforma a un GET
		if isinstance(url_or_request, str):  
			request = Request.get(url_or_request)
		else: 
			request = url_or_request

		self._on_preload()

		count = 0

		while count <= retries:
			try:
				if max_time == None:
					max_time = self.__context.options.max_time_load_page					   
				if max_time == None:
					return self._load_page(request)
				else:
					return self.__timeout_func(
											self._load_page,
											max_time,
											[request]
											)
			except Exception as ex:
				if count == retries:
					raise ex
				
				# TODO no cambiar si ya se cambió el proxy
				self.__context.proxies.change()
				sleep(sleep_time)
				count += 1
				import traceback;traceback.print_exc()
								
			else:
				break
		
	
	def _download(self, url):
		"Retorna el contenido de un archivo resultado de hacer un GET"
		raise NotImplementedError
	
	def download(self, url, destination, dir = False):
		"""
		Descarga un archivo de la url dada a un destino dado creando el
		directorio donde descargar el archivo.
		
		Si dir es True destination indica el directorio a guardar y el nombre
		del archivo se escoje a partir de la url.
		
		Si dir es False destination se trata como el nombre y se guarda con el 
		nombre especificado.
		"""
		# los caracteres a reemplazar en los nombres de archivo en windows
		windows_forbidden_chars = '\:*<>|?"/' 
		
		check_if_any_type(destination, str)
		check_if_any_type(url, str)
		
		downloaded_data = self._download(url)
		
		if dir:
			parts = urlparse(url)
			file_name = parts[2].split('/')[-1] # el último path
			
			# reemplaza caracteres prohibidos
			for char in windows_forbidden_chars: 
				file_name = file_name.replace(char, '-')
			
			destination += os.path.sep + file_name

		# crea el directorio padre
		dirname = os.path.dirname(destination)
		if dirname == '':
			pass # no se crea si el directorio es el actual
		elif os.path.exists(dirname): 
			if not os.path.isdir(dirname):
				raise ValueError("file already exists, but not a directory")
		else:
			os.makedirs(dirname)
			
		local = open(destination, "wb")
		local.write(downloaded_data)
		local.close()
	
	## {{{ http://code.activestate.com/recipes/473878/ (r1)
	def __timeout_func(self, func, timeout_duration, args=(), kwargs={}):
		"Llama una función con un tiempo límite"
		class InterruptableThread(threading.Thread):
			def __init__(self):
				threading.Thread.__init__(self)
				self.result = None
				self.exception_raised = None
	
			def run(self):
				try:
					self.result = func(*args, **kwargs)
				except Exception as ex:
					self.exception_raised = ex
	
		it = InterruptableThread()
		it.daemon = False
		it.name = "TimeoutThread-%s" % func.__name__
		it.start()
		it.join(timeout_duration)
#		entra al raise ValueError
		if it.isAlive(): # timeout
			raise ValueError("Timeout expired for call")
		elif it.exception_raised == None:
			return it.result # salió sin error
		else: 
			raise it.exception_raised # salió con error

	def get_url(self):
		raise NotImplementedError
	
	@property
	def url(self):
		"Devuelve la url de la página actual"
		return self.get_url()
	
	@property
	def encoding(self):
		"""
		Encoding para el browser. Puede ser un valor cualquiera como 'utf-8',
		'iso-8859-1' o 'auto' para la autodetección del encoding.
		"""
		return self.__encoding

	@encoding.setter
	def encoding(self, value):
		check_if_any_type(value, str)
		self.__encoding = value
	


class PreloadPageListener(object):
	"Modela un escucha de carga de la página"
	def on_load_page(self, browser):
		"Se llama al cargar una página"
		raise NotImplementedError
	