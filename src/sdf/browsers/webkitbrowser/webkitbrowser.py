# *- encoding:utf-8 -*

__author__="igui"
__date__ ="$09/04/2009 08:01:39 PM$"

from types import NoneType
from PyQt4 import QtCore
from PyQt4 import QtWebKit
from PyQt4.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkProxy, \
	QNetworkAccessManager, QNetworkCookie
from .dom import DOM
import threading
from .. import browser
from .cookiejar import CookieJar
from .page import Page
from sdf.exception import LoadPageError
from sdf.util.typecheck import check_if_any_type
from sdf.helpers import UrlHelper
from sdf.browsers.proxy import ProxyListener

class WebKitBrowser(DOM, browser.Browser):
	"""
	Es un mini de un navegador web
	Usada para navegar páginas de forma más fácil que haciendo requests http
	
	.. image:: images/webkitbrowser.png
	"""
	def __init__(self, context, show_images, javascript, webview):
		"Inicia el navegador en una página dada"
		DOM.__init__(self)
		browser.Browser.__init__(self, context)

		self.__web_view = webview
		
		# inicia la vista de la página
		self.__page = Page(self.__web_view, self.__web_view)
		self.__web_view.setPage(self.__page)

		# dice si se muestran imágenes o no
		self.set_show_images(show_images)
		
		# habilita algunas opciones extra
		settings = {
				QtWebKit.QWebSettings.JavascriptCanOpenWindows 		: True,
				QtWebKit.QWebSettings.JavascriptCanAccessClipboard	: True,
				QtWebKit.QWebSettings.DeveloperExtrasEnabled 		: True,
				QtWebKit.QWebSettings.PluginsEnabled		 		: True,
				QtWebKit.QWebSettings.JavaEnabled		 			: True,
				QtWebKit.QWebSettings.JavascriptEnabled				: javascript,
		}
		
		for setting, setting_value in list(settings.items()):
			self.__page.settings().setAttribute(setting, setting_value)

		self.__cookie_jar = CookieJar(self, accept_cookies = True)
		self.__page.networkAccessManager().setCookieJar(self.__cookie_jar)

		# usada para esperar que termine de cargar la página
		self.__page_load_condition = threading.Condition()
		self.__page_load_request = None
		self.__page_load_result = False;
		self.connect(self.__page, QtCore.SIGNAL('loadFinished(bool)'),
			self, QtCore.SLOT('__page_load_finished_slot(bool)') )
		self.connect(self, QtCore.SIGNAL('page_load_signal(void)'),
			self.__page_load_slot)
		
		# usada ir atrás
		self.connect(self, QtCore.SIGNAL('back_signal(void)'),
			self.__web_view, QtCore.SLOT('back(void)') )
		
		# usada ir adelante
		self.connect(self, QtCore.SIGNAL('forward_signal(void)'),
			self.__web_view, QtCore.SLOT('forward(void)') )
		
		# usada para parar el browser
		self.connect(self, QtCore.SIGNAL('stop_signal(void)'),
			self, QtCore.SLOT('__stop_slot(void)') )
		self.__stop_condition = threading.Condition()
		
		# usado para esperar una url dada
		self.__request_finished_condition = threading.Condition()
		self.__request_finished_result = None
		self.connect(self.__web_view.page().networkAccessManager(), 
			QtCore.SIGNAL('finished (QNetworkReply *)'),
			self.__request_finished_slot) 
		
		# usado para cargar una url
		self.__download_condition = threading.Condition()
		self.__download_res = None
		self.__download_manager = None # el manager que hace la descarga
		self.connect(self, QtCore.SIGNAL('download_signal(QString)'),
			self.__download_slot)
		
		# usado para setear un proxy
		self.__set_proxy_condition = threading.Condition()
		self.connect(self, QtCore.SIGNAL('set_proxy_signal(QString, int)'),
			self.__set_proxy_slot)
		
		# setea el proxy
		proxy = context.proxies.get_current()
		self.__set_proxy_slot(proxy.host, proxy.port)
		context.proxies.add_change_listener(_ProxyListener(self))
		
		# custom headers
		self.__custom_headers = {
		}
		
	def get_view(self):
		return self.__web_view
	
	def _load_page(self, request):
		"Carga una página y retorna cuando ya esté cargada"
		self.__page_load_condition.acquire()
		
		request.url = str(request.url)
		self.__page_load_request = request
	
		self.emit(QtCore.SIGNAL('page_load_signal(void)'))
		
		self.__page_load_condition.wait()
		if not self.__page_load_result:
			self.__page_load_condition.release()
			raise LoadPageError('Error loading page.')				
		self.__page_load_condition.release()

	def eval_js_and_block(self, script, throw_exceptions = False):
		"""
		Evalúa un script en javascript en la página y retorna solo cuando la
		página esté cargada
		"""
		self.__page_load_condition.acquire()
		result = self.eval_js(script, throw_exceptions)
		self.__page_load_condition.wait()
		if not self.__page_load_result:
			self.__page_load_condition.release()
			raise LoadPageError('Error loading page.')
		self.__page_load_condition.release()
		return result
		
	def wait_load_page(self):
		"Bloquea al hilo y retorna cuando la página termine de cargar"
		self.__page_load_condition.acquire()
		self.__page_load_condition.wait()
		self.__page_load_condition.release()
		
	def wait_for_resource(self, url):
		"Bloquea hasta que se cargue cierto recurso"
		
		self.__request_finished_condition.acquire()
		while True:
			self.__request_finished_condition.wait()
			reply = self.__request_finished_result
			if reply.url().toString().__str__() == url:
				break
		self.__request_finished_condition.release()
	
	def __request_finished_slot(self, reply):
		self.__request_finished_condition.acquire()
		self.__request_finished_result = reply
		self.__request_finished_condition.notifyAll()
		self.__request_finished_condition.release()
	
	def eval_js(self, script, throw_exceptions = False):
		"Evalúa un script en javascript sobre el frame principal de la página"
		return self.get_main_frame().eval_js(script, throw_exceptions)

	@QtCore.pyqtSignature("void")
	def __page_load_slot(self):
		with self.__page_load_condition:
			request = self.__page_load_request
		
		# setea la operación
		if request.method == 'GET':
			operation = QNetworkAccessManager.GetOperation
		elif request.method == 'POST':
			operation = QNetworkAccessManager.PostOperation
		else:
			raise ValueError("Unsupported method %s" % request.method)
		
		user_agent = None # el user agent para el request
		
		# Si se definieron headers personalizados se setean tambien
		qnetworkrequest =QNetworkRequest(UrlHelper.from_user_input(request.url))
		for header, value in list(self.__custom_headers.items()):
			qnetworkrequest.setRawHeader(header, value)
			if header.lower() == 'user-agent':
				user_agent = value
		
		# setea url y headers 
		qnetworkrequest =QNetworkRequest(UrlHelper.from_user_input(request.url))
		for header, value in list(request.headers.items()):
			qnetworkrequest.setRawHeader(header, value)
			if header.lower() == 'user-agent':
				user_agent = value
				
		
		self.__page._set_user_agent(user_agent)					
		
		# lo más importante: carga la página
		self.__web_view.load(qnetworkrequest, operation, request.body)
		

	@QtCore.pyqtSignature("bool")
	def __page_load_finished_slot(self, result):
		"Llamado cuando la página termina de cargar"
		self.__page_load_condition.acquire()
		self.__page_load_request = None
		self.__page_load_result = result
		self.__page_load_condition.notifyAll()
		self.__page_load_condition.release()

	def get_html(self):
		"Retorna el contenido de la página"
		return self.__page.mainFrame().toHtml().__str__()

	def get_cookies_for_url(self, url):
		"Retorna las cookies que el navegador mandaría al requerir una url dada"
		url = QtCore.QUrl(url)
		return self.__page.networkAccessManager().cookieJar().cookiesForUrl(url)

	def add_cookies_for_url(self, cookies, url):
		"""
		Agrega las cookies de cookies para poder ser mandadas en un request a
		url
		"""
		cookie_list = []
		for c in cookies:
			if isinstance(c, dict):
				cookie_list.append(QNetworkCookie(c['name'], c['value']))
			else:
				return self.__cookie_jar.setCookiesFromUrl(cookies, QtCore.QUrl(url))
		return self.__cookie_jar.setCookiesFromUrl(cookie_list, QtCore.QUrl(url))		

	def get_url(self):
		"retorna la url actual"
		return self.__web_view.url().toString().__str__()
	
	def set_show_images(self, show):
		"Dice si se van a mostrar las imágenes o no"
		show_imagesAttr = QtWebKit.QWebSettings.AutoLoadImages
		self.__page.settings().setAttribute(show_imagesAttr, show)
		
	def refresh(self):
		"Recarga la página"
		print("Reload")
		self.__page.triggerAction(QtWebKit.QWebPage.Reload)

	def back(self):
		self.emit(QtCore.SIGNAL('back_signal(void)'))
		self.wait_load_page()
		
	def stop(self):
		"Para el browser"
		self.__stop_condition.acquire()
		self.emit(QtCore.SIGNAL('stop_signal(void)'))
		self.__stop_condition.wait()
		self.__stop_condition.release()
	
	@QtCore.pyqtSignature("void")
	def __stop_slot(self):
		self.__web_view.stop()
		self.__stop_condition.acquire()
		self.__stop_condition.notifyAll()
		self.__stop_condition.release()
		
	def forward(self):
		self.emit(QtCore.SIGNAL('forward_signal(void)'))
		self.wait_load_page()

	def open_link(self, x, y):
		self.get_main_frame().open_link(x, y)
		
	def get_main_frame(self):
		"Devuelve el frame principal de la página mostrada"
		return self.__page.main_frame
	
	def deactivate_javascript(self):
		setting = QtWebKit.QWebSettings.JavascriptEnabled
		self.__page.settings().setAttribute(setting, False)
	
	def activate_javascript(self):
		setting = QtWebKit.QWebSettings.JavascriptEnabled
		self.__page.settings().setAttribute(setting, True)
	
	@QtCore.pyqtSignature("bool")
	def __slot_ver_imagenes(self, show):
		self.set_show_images(show)
		
	@property
	def custom_headers(self):
		"""
		Diccionario que contiene headers personalizados que se deseen usar en cada
		pedido realizado por el browser.
		
		Por ejemplo: ::
		
			browser.custom_headers = {
				'Accept-Encoding':'gzip,deflate',
				'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
			}
		"""
		return self.__custom_headers
	
	@property
	def cookies_enabled(self):
		"Se usa para setear (o no) las cookies del navegador"
		return self.__cookie_jar.accept_cookies
	
	@property
	def js_alert_enabled(self):
		"Habilita los alert de javascript"
		return not self.__page.disable_alert
	
	@js_alert_enabled.setter
	def js_alert_enabled(self, val):
		self.__page.disable_alert = not val
	
	@cookies_enabled.setter
	def cookies_enabled(self, value):
		check_if_any_type(value, bool)
		self.__cookie_jar.accept_cookies = value
		
	@custom_headers.setter
	def custom_headers(self, value):
		check_if_any_type(value, dict)
		self.__custom_headers = value
	
	def clear_cookies(self):
		"Borra todas las cookies del navegador"
		self.__cookie_jar.setAllCookies([])
		
	def get_frame(self, url = None, name = None):
		"""
		Devuelve un objeto Frame hijo del browser con una url dada o nombre.
		Este frame puede ser usado para buscar elementos, etc sin salir de la
		página. Si se tiene una página web como esta:
		
		.. code-block:: html
			
				<html><body>
					<iframe name="feisbuc" src="http://www.facebook.com/"/>
				</body></html>

		Se puede hacer lo siguiente para buscar algo en el frame: ::
		
			# obtiene el frame de facebook
			# o bien frame = browser.get_frame(url='http://www.facebook.com/')
			frame = browser.get_frame(name='feisbuc')
								
			# busca un div en el frame de facebook
			print frame.find(text_contains = 'te ayuda').innerHTML
			# imprime Facebook te ayuda a comunicarte y compartir con las personas que conoces.
		
		"""
		check_if_any_type(url, [str, NoneType])
		check_if_any_type(name, [str, NoneType])
		return self.get_main_frame().get_frame(url, name)
	
	def _download(self, url):
		self.__download_condition.acquire()
		self.emit(QtCore.SIGNAL('download_signal(QString)'), str(url))
		self.__download_condition.wait()
		res = self.__download_res
		self.__download_condition.release()
	
		if res == None:
			raise LoadPageError("Couldn't load url %s" % url)
		
		return res
	
	def __download_slot(self, url):
		manager = self.__web_view.page().networkAccessManager();
		self.__download_manager = manager
		self.connect(manager,
			QtCore.SIGNAL("finished(QNetworkReply*)"),
			self.__download_finished_slot
		)		
		manager.get(QNetworkRequest(UrlHelper.from_user_input(url)));
		
	def __download_finished_slot(self, qnetworkreply):
		self.__download_condition.acquire()
		if qnetworkreply.error() != QNetworkReply.NoError:
			self.__download_res = None
		else:
			self.__download_res = qnetworkreply.readAll()
		
		self.disconnect(self.__download_manager,
			QtCore.SIGNAL("finished(QNetworkReply*)"),
			self.__download_finished_slot
		)		

		self.__download_manager = None
		
		self.__download_condition.notifyAll()
		self.__download_condition.release()
		
		qnetworkreply.deleteLater()
		
	def set_proxy(self, host = "", port = 80):
		"Pone el proxy HTTP en cierto host y puerto dado"
		self.__set_proxy_condition.acquire()
		self.emit(QtCore.SIGNAL('set_proxy_signal(QString, int)'), host, port)
		self.__set_proxy_condition.wait()
		self.__set_proxy_condition.release()
		
	def __set_proxy_slot(self, host, port):
		proxy = QNetworkProxy()
		
		if not host:
			proxy.setType(QNetworkProxy.NoProxy)
		else:
			proxy.setType(QNetworkProxy.HttpProxy)
			proxy.setHostName(host)
			proxy.setPort(port)
			self.__web_view.page().networkAccessManager().setProxy(proxy)
			
		self.__set_proxy_condition.acquire()
		self.__set_proxy_condition.notifyAll()
		self.__set_proxy_condition.release()
	
class _ProxyListener(ProxyListener):
	"Listener para WebKitBrowser"
	def __init__(self, browser):
		ProxyListener.__init__(self)
		self.__browser = browser
		
	def on_proxy_change(self, proxy):
		"Se llama al cambiar el proxy"
		self.__browser.set_proxy(proxy.host, proxy.port)
		
	