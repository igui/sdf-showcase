# *- coding: utf-8 -*
'''
Created on 21/07/2009

@author: Ignacio
'''

from PyQt4.QtWebKit import QWebPage
from PyQt4 import QtCore
from sdf.exception import LogicError
from threading import Condition
from threading import Lock
from .frame import Frame
from sdf.util.typecheck import check_if_any_type
from types import NoneType


class Page(QWebPage):
	"Representa una página de un webkitbrowser"
	
	def __init__(self, browser, parent):
		"Inicia una página web, el padre debe ser el widget que lo contiene"
		QWebPage.__init__(self, parent)
		
		self.__browser = browser
				
		# variables para crear frame
		self.__get_frame_condition = Condition(Lock())
		self.__get_frame_result = None 
		self.connect(self, QtCore.SIGNAL('get_frame_signal(QWebFrame *)'),
			self, QtCore.SLOT('__get_frame_slot(QWebFrame *)') )
		
		self.__main_frame = None
		self.__user_agent = None
		
		self.disable_alert = False
		"Hace que se deshabilite el alert de javascript"
		
	@property
	def main_frame(self):
		if self.__main_frame == None:
			self.__main_frame = self.__get_main_frame()
		return self.__main_frame
	
	def javaScriptAlert(self, frame, msg):
		"Condicionalmente muestra la ventana de javascript"
		if not self.disable_alert:
			return QWebPage.javaScriptAlert(self, frame, msg)
	
	
	def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
		"""
		This function is called whenever a JavaScript program tries to print
		a message to the web browser console.
		"""
		
		unknown_source = sourceID == 'undefined' or sourceID == None
		unknown_source = unknown_source or sourceID == ' ' 
		
		if unknown_source: # source desconocido
			sourceLine = "Line %d" % lineNumber# pone solo la info de línea
		else:
			sourceLine = "Source %s, line %d" % (sourceID, lineNumber) 
		
		# imprime el mensaje y emite la señal con ese mensaje
		msg = "%s: %s" % (sourceLine, message)
		self.emit(QtCore.SIGNAL('signaljavaScriptConsoleMessage(QString)'), msg)

	
	def __get_main_frame(self):
		"Retorna el frame principal"
		qwebframe = self.mainFrame()
		
		self.__get_frame_condition.acquire()
		self.emit(QtCore.SIGNAL('get_frame_signal(QWebFrame *)'), qwebframe)
		self.__get_frame_condition.wait()
		if self.__get_frame_result == None:
			self.__get_frame_condition.release()
			raise LogicError("Couldn't get WebKitBrowser instance")
		else:
			self.__get_frame_condition.release()
			res = self.__get_frame_result
			self.__get_frame_result = None
			return res
	
	
	@QtCore.pyqtSignature("QWebFrame *")
	def __get_frame_slot(self, qwebframe):
		"Hace el trabajo de crear el browser de WebKit"
		self.__get_frame_condition.acquire()
		try:
			self.__get_frame_result = Frame(self.__browser, qwebframe, self)
		except:
			self.__get_frame_result = None
			import traceback;traceback.print_exc()
		self.__get_frame_condition.notifyAll()
		self.__get_frame_condition.release()
	
	def _set_user_agent(self, ua):
		"Setea el user agent para los requests"
		check_if_any_type(ua, [str, NoneType])
		self.__user_agent = ua
		
	def userAgentForUrl(self, url):
		"Da el header User-Agent para cierta url"
		if self.__user_agent == None:
			return QWebPage.userAgentForUrl(self, url)
		else:
			return self.__user_agent
	