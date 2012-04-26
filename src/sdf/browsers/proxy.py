# *- encoding: utf-8 -*
'''
Created on 19/07/2010

@author: iavas
'''
import csv
from random import choice
from sdf.util.typecheck import check_if_any_type

class ProxyManager(object):
	'''
	Maneja los proxies que usan los browsers de SDF
	'''
	
	def __init__(self, context, proxy_file = None):
		self.__change_listeners = []
		self.__context = context
		
		if not proxy_file: 
			self.__proxies = [ NoProxy() ]
		else:
			self.__proxies = []
			reader = csv.reader(open(proxy_file), delimiter=';')
			for row in reader:
				try:
					self.__proxies.append( Proxy(row[0], int(row[1])) )
				except ValueError:
					pass
			
		self.__current_proxy = choice(self.__proxies)
		if isinstance(self.__current_proxy, Proxy):
			p = self.__current_proxy
			context.logger.log("Usando proxy %s:%d" % (p.host, p.port))
			
	def get_current(self):
		"Da un objeto BaseProxy con el proxy actual"
		return self.__current_proxy
	
	def change(self):
		"""
		Cambia el proxy actual para todos los browsers del parser. El Proxy se
		elige al azar entre la lista de proxies de las opciones.
		"""
		self.__current_proxy = choice(self.__proxies)
		if isinstance(self.__current_proxy, Proxy):
			p = self.__current_proxy
			self.__context.logger.log("Usando proxy %s:%d" % (p.host, p.port))
			
		for l in self.__change_listeners:
			l.on_proxy_change(self.__current_proxy)
	
	def add_change_listener(self, listener):
		"""
		Agrega un escucha al cambio de proxy donde listener es un objeto del
		tipo
		:class:`ProxyListener <sdf.browsers.proxy.ProxyListener>`
		"""		
		self.__change_listeners.append(listener)
	

class BaseProxy(object):
	"Clase base de proxies"
	pass

class NoProxy(BaseProxy):
	"Un objeto que representa comunicación directa sin proxy"
	def __init__(self):
		BaseProxy.__init__(self)
		
	@property
	def host(self):
		"Devuelve ''"
		return ''
	
	@property
	def port(self):
		"Devuelve 0"
		return 0
		
	def __repr__(self):
		return "NoProxy"

class Proxy(BaseProxy):
	"Datos de un proxy HTTP"
	
	def __init__(self, host, port):
		check_if_any_type(host, str)
		check_if_any_type(port, [int,int])
		
		BaseProxy.__init__(self)
		self.__host = host
		self.__port = port
	
	@property
	def host(self):
		"El host del proxy"
		return self.__host
	
	@property
	def port(self):
		"El puerto del proxy"
		return self.__port
	
	def __repr__(self):
		return "Proxy host: %s, port: %d" % (self.__host, self.__port)


class ProxyListener(object):
	"Escucha el cambio de un proxy"
	
	def on_proxy_change(self, proxy):
		"Se llama al cambiar el proxy, proxy es un objeto del tipo :class:`BaseProxy <sdf.browsers.proxy.BaseProxy>`"
		raise NotImplementedError
