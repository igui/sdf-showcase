# *- coding: utf-8 -*
'''
Created on 20/07/2009

@author: Ignacio
'''

from .dom import DOM
from PyQt4.QtCore import QVariant, QPoint
from PyQt4 import QtCore
import threading
from sdf.exception import JavaScriptError


class Frame(DOM, QtCore.QObject):
	'''
	Representa un frame de una página web
	'''
	def __init__(self, browser, qwebframe, parent):
		'''
		Inicia el frame a partir de un webframe dado 
		una instancia de webkitbrowser dada. No debe llamarse públicamente
		'''
		DOM.__init__(self)
		QtCore.QObject.__init__(self, parent)
		
		self.__webframe = qwebframe
		self.__browser = browser

		# para evaluar javascript
		self.__eval_js_condition = threading.Condition()
		self.__eval_js_res = None
		self.__eval_js_error = None
		self.connect(self, QtCore.SIGNAL('signalEvalJS(QString)'),
			self.__eval_js_slot)
		
		# para cambiar la posición de la acción
		self.__upostda_condition = threading.Condition()
		self.connect(self, QtCore.SIGNAL('signalUPosDA(QPoint *)'),
			self.__uposda_slot)
		
		# para crear las frames hijas
		self.__get_child_frame = threading.Condition()
		self.__get_child_frame_res = None
		self.connect(
					self,
					QtCore.SIGNAL('signalGetChildFrame(QString, QString)'),
					self.__get_child_frame_slot
					)
		
	def get_frame(self, url = None, name = None):
		"""
		Devuelve una frame con una url dada o nombre dado hijo del frame actual.
		Si url es None y name es None, se devuelven todas las frames hijas
		"""
		if not url:
			url = ''
		if not name:
			name = ''
	
		self.__get_child_frame.acquire()
		self.emit(
				QtCore.SIGNAL('signalGetChildFrame(QString, QString)'),
				url,
				name
				)
		self.__get_child_frame.wait()
		res = self.__get_child_frame_res
		self.__get_child_frame.release()
		
		if res == None:
			raise ValueError("Frame not found")
		return res		
		
	def get_html(self):
		"Devuelve una cadena con el texto del html mostrado"
		return self.__webframe.toHtml().__str__()
	
	def get_url(self):
		return self.__webframe.url().toString().__str__()
		
	def eval_js(self, script, throw_exceptions = False):
		"Evalúa un script javascript en el frame"
		

		javascript_signal = QtCore.SIGNAL('signaljavaScriptConsoleMessage(QString)')
		
		self.__eval_js_condition.acquire()
		
		self.__eval_js_error = None # reinicia el error
		self.connect(self.__webframe.page(), javascript_signal,
			self.__slot_js_console_message)
		
		self.emit(QtCore.SIGNAL('signalEvalJS(QString)'), script)
		
		self.__eval_js_condition.wait()
		self.disconnect(self.__webframe.page(), javascript_signal,
			self.__slot_js_console_message)		
		res = self.__eval_js_res
		self.__eval_js_condition.release()
		
		# si hubo un error al evaluar lo tira
		if self.__eval_js_error != None and throw_exceptions:
			raise self.__eval_js_error #IGNORE:E0702
		return self.__convert_qvariant_to_python(res)

	def open_link(self, x, y):
		self.__upostda_condition.acquire()
		p = QPoint()
		p.setX(int(x))
		p.setY(int(y))
		self.emit(QtCore.SIGNAL('signalUPosDA(QPoint *)'), p)
		self.__upostda_condition.wait()
		self.__upostda_condition.release()
		
	def wait_load_page(self):
		self.__browser.wait_load_page()
		
	def get_name(self):
		"The name of this frame as defined by the parent frame."
		return self.__webframe.frameName().__str__()
		
	def __eval_js_slot(self, script):
		"Usado para evaluar javascript"
		self.__eval_js_res = None # resetea el resultado anterior
		self.__eval_js_condition.acquire()
		# evalúa el javascript
		self.__eval_js_res = self.__webframe.evaluateJavaScript(script)
		self.__eval_js_condition.notify_all()
		self.__eval_js_condition.release()
		
	def __slot_js_console_message(self, message):
		self.__eval_js_error = JavaScriptError(message.__str__())		

	
	def __convert_qvariant_to_python(self, qvariant):
		"Intenta convertir un QVariant a un objeto que sea nativo de python"

		if qvariant.type() == QVariant.Invalid:
			return None
		elif qvariant.type() == QVariant.Bool:
			return qvariant.toBool()
		elif qvariant.type() == QVariant.Double:
			return qvariant.toDouble()[0]
		elif qvariant.type() == QVariant.String:
			return qvariant.toString().__str__()
		else:
			return None

	def __uposda_slot(self, pos):
		"Actualiza la posición de las acciones dependientes de la página"
		self.__upostda_condition.acquire()
		p = self.__webframe.page()
		p.updatePositionDependentActions(pos)
		p.triggerAction(p.OpenLink)
		self.__upostda_condition.notify()
		self.__upostda_condition.release()

	
	def __get_child_frame_slot(self, url, name):
		"Da el frame si es igual a la url y nombre que se pasa como parámetro"
		self.__get_child_frame.acquire()
		
		if not url and not name:
			# se devuelven todas las urls
			self.__get_child_frame_res = [
				Frame(self.__browser, w, self)
				for w in self.__webframe.childFrames()
			]
		else:
			# se devuelve el frame que tenga el nombre y/o la url que se 
			# pasó como parámetro
			for w in self.__webframe.childFrames():
				if (not url or w.url().toString() == url) and \
					(not name or w.frameName() == name):
					self.__get_child_frame_res = Frame(self.__browser, w, self)
					break # se encontró el frame
				else:
					self.__get_child_frame_res = None # No se encontró el frame
		
		self.__get_child_frame.notifyAll()
		self.__get_child_frame.release()
		
		
	def __repr__(self):
		name = self.get_name()
		url = self.get_url()
		
		if name[0:4] == '<!--': # no tiene nombre
			return "<Frame url='%s'>" % url
		else:
			return "<Frame name='%s' url='%s'>" % (name, url)
	