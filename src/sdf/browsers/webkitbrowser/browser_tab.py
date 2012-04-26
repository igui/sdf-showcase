# *- encoding: utf-8 -*
'''
Created on 09/08/2010

@author: iavas
'''
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import SIGNAL, SLOT
from .uiwebviewtab import Ui_webViewTab
from .webkitbrowser import WebKitBrowser


class BrowserTab(QWidget):
	"Representa un tab del browser"
	
	def __init__(self, parent, context, show_images):
		QWidget.__init__(self, parent)
		
		self.__ui = Ui_webViewTab()
		self.__ui.setupUi(self)
		self.__browser_main_window = parent
	
		web_view = self.__ui.webView
		
		# acciones para la barra de progresp
		self.__ui.cargandoProgressBar.hide()
		self.connect(web_view, SIGNAL('loadStarted()'),
			self.__slot_load_started)
				
		self.connect(web_view, SIGNAL('loadProgress (int)'),
			self.__ui.cargandoProgressBar, SLOT('setValue(int)'))
		self.connect(
			web_view, SIGNAL('loadFinished(bool)'),
			self.__slot_finish_load)
	
		# acciones sobre el título
		self.connect(
			web_view, SIGNAL('titleChanged(const QString&)'),
			self.__slot_refresh_title
			)
		
		# acciones sobre la url
		self.connect(web_view, SIGNAL('urlChanged (const QUrl&)'),
					self.__slot_url_changed)
		
		# estado del browser
		self.__show_images = show_images
		self.__statusbar = ''
		self.__title = '(Vacía)'
		self.__urlbar = ''
		
		self.__browser = WebKitBrowser(context, show_images, True, web_view)

	@property
	def browser(self):
		return self.__browser
	
	@property
	def show_images(self):
		return self.__show_images
	
	@property
	def statusbar_msg(self):
		return self.__statusbar
	
	@property
	def urlbar(self):
		return self.__urlbar
	
	@urlbar.setter
	def urlbar(self, val):
		self.__urlbar = val
	
	@property
	def title(self):
		return self.__title
	
	@property
	def webview(self):
		return self.__ui.webView
	
	def set_show_images(self, show_images):
		self.__show_images = show_images
		self.__browser.set_show_images(show_images)
		
	def __slot_finish_load(self, ok):
		"Indica que terminó la carga de una página"
		if ok:
			msg = 'Listo'
			#self.setWindowIcon(self.__webView.icon())
		else:
			msg = 'Ocurrió un error al cargar la página'
		self.__ui.cargandoProgressBar.hide()
		self.__statusbar = msg
		self.__browser_main_window.statusbar_changed(self, msg)

	def __slot_refresh_title(self, title):
		"Se refresca el título"
		self.__title = title
		self.__browser_main_window.title_changed(self, title, True)
		
	def __slot_url_changed(self, url):
		"Se llama cuando cambia la url"
		self.__urlbar = url.toString()
		self.__browser_main_window.url_changed(self, url)
	
	def __slot_load_started(self):
		self.__ui.cargandoProgressBar.show()
		self.__browser_main_window.title_changed(self, "Cargando...", False)
	