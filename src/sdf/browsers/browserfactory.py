# *- encoding: utf-8 -*

'''
Created on 08/07/2009

@author: Ignacio
'''


from sdf.exception import LogicError
from threading import Condition
from threading import Lock
from PyQt4 import QtCore
from sdf import Context, options, DataAdapter
from .basicbrowser import BasicBrowser
from sdf.browsers.webkitbrowser import BrowserMainWindow
from sdf.util import Enum
from PyQt4.QtNetwork import QSslConfiguration, QSslSocket
from sdf.browsers.bootstrap import BootStrap

class BrowserFactory(QtCore.QObject):
	'''
	Una fábrica de browsers
	'''
	
	# La instancia del singleton
	__instance = None 
	
	browser_type = Enum('BasicBrowser', 'WebKitBrowser', 'DefaultBrowser')
	"""
	Enumerado para indicar el tipo de browser, toma los valores
	
	* *BasicBrowser* para BasicBrowser
	* *WebKitBrowser* para WebKitBrowser
	* *DefaultBrowser* para denotar al browser usado por defecto
	"""
		
	def __init__(self, context):
		QtCore.QObject.__init__(self)
				
		self.__context = context
				
		# variables para la funcion getWebKitBrowser
		self.__get_webkitbrowser_result = None 
		self.__get_webkitbrowser_condition = Condition(Lock())
		self.connect(self, QtCore.SIGNAL('get_webkitbrowser_signal(bool, bool)'),
			self, QtCore.SLOT('__get_webkitbrowser_slot(bool, bool)') )
		
		self.__webkitbrowser_mainwindow = None
		
	@staticmethod
	def create_instance(context=None):
		"""
		Inicializa la instancia, este método debe llamarse antes que 
		getInstance() y debe llamarse por el hilo de la aplicación QT
		"""
		
		if context is None:
			class DummyDataAdapter(DataAdapter):
				pass
			o = options.Options()
			o.data_adapter_class = DummyDataAdapter
			context = Context(o)
		
		BrowserFactory.__instance = BrowserFactory(context) 
		
		# deshabilita la verificación de certificados SSL
		ssl =  QSslConfiguration.defaultConfiguration()
		ssl.setPeerVerifyMode(QSslSocket.VerifyNone)
		QSslConfiguration.setDefaultConfiguration(ssl)
	
	@staticmethod
	def get_instance():
		"Devuelve una instancia de la fábrica de browsers"
		if BrowserFactory.__instance == None:
			error = "BrowserFactory "
			error += "instance must be initialized before calling this method"
			raise LogicError(error)
		return BrowserFactory.__instance

	def get_webkitbrowser(self, show, show_images):
		"Devuelve un objeto de la clase WebKitBrowser llamando a su constructor"
		self.__get_webkitbrowser_condition.acquire()
		
		BootStrap.init_qt()	
		
		self.emit(QtCore.SIGNAL('get_webkitbrowser_signal(bool, bool)'),
				show, show_images)
		self.__get_webkitbrowser_condition.wait()
		if self.__get_webkitbrowser_result == None:
			self.__get_webkitbrowser_condition.release()
			raise LogicError("Couldn't get WebKitBrowser instance")
			
		else:
			self.__get_webkitbrowser_condition.release()
			return self.__get_webkitbrowser_result
		
	def get_basicbrowser(self):
		"Retorna una nueva instancia de un BasicBrowser"
		return BasicBrowser(self.__context)
	
	def get_mozillabrowser(self):
		"Retorna una instancia de un MozillaBrowser"
		
		# FIXME todavía no hace nada, solo levanta la aplicación XULRunner
		BootStrap.init_mozilla()
		return MozillaBrowser(self.__context)
	
	@QtCore.pyqtSignature("bool, bool")
	def __get_webkitbrowser_slot(self, show, show_images):
		"Hace el trabajo de crear el browser de WebKit"
				
		self.__get_webkitbrowser_condition.acquire()
		
		try:
			if self.__webkitbrowser_mainwindow == None:
				self.__webkitbrowser_mainwindow = BrowserMainWindow(
														self.__context,
														show,
														show_images
														)
				
			mw = self.__webkitbrowser_mainwindow
			res = mw.create_webkitbrowser(self.__context, show_images, True)
			self.__get_webkitbrowser_result = res

		except LogicError:
			self.__get_webkitbrowser_result = None
			import traceback;traceback.print_exc()
			
		self.__get_webkitbrowser_condition.notifyAll()
		self.__get_webkitbrowser_condition.release()
		
		