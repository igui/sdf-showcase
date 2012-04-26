# *- coding: utf-8 -*
'''
Created on 10/07/2009

@author: Ignacio Avas
'''
from PyQt4.QtGui import QMainWindow, QKeySequence, QTabBar
from PyQt4.QtCore import SIGNAL, QUrl
from PyQt4.QtWebKit import QWebPage
from .uiwebkitbrowser import Ui_WebKitBrowser
from .console import Console
from sdf.helpers import UrlHelper
from sdf import Properties
from .browser_tab import BrowserTab
from threading import Lock
from .close_button import CloseButton
from .tab_icon import TabIcon

class BrowserMainWindow(QMainWindow):
	'''
	Representa la ventana que tiene el browser, tiene todo el comportamiento
	del UI pero no implementa la interface browser
	'''
	def __init__(self, context, show, show_images):
		QMainWindow.__init__(self)
		
		self.__context = context
		
		self.__ui = Ui_WebKitBrowser()
		self.__ui.setupUi(self)
		
		self.__ui.imagenesPushButton.setChecked(show_images)
		self.__ui.consoleDock.hide()
		
		initial_tab = BrowserTab(self, context, show_images)
		self.__ui.tabWebViews.addTab(initial_tab, TabIcon(), initial_tab.title)
		self.__initial_tab_used = False
		self.__initial_tab = initial_tab
		self.__browser_create_lock = Lock()
		
		# inicializa las acciones del browser
		self.__back_action = None
		self.__refresh_action = None
		self.__forward_action = None
		self.__replace_actions(initial_tab)
		
		# Para que muestre el título bien
		self.__update_title('')
				
		self.__ui.consoleDock.setWidget(Console(self,
				{ 'browser': initial_tab.browser }))
		
		
		self.setup_ui(show)

	def setup_ui(self, show):
		"Setea los detalles de la UI"
		if show:
			self.show()
			
		# acciones para cargar una página
		self.connect(
					self.__ui.direccionlineEdit,
					SIGNAL('returnPressed()'),
					self.__slotCargarURL
					)
		
		# acciones sobre la barra de dirección
		self.connect(
					self.__ui.direccionlineEdit,
					SIGNAL('textEdited(const QString&)'),
					self.__slot_locationbar_changed
			)
					
		# acciones sobre el botón de ver imágenes
		self.connect(
					self.__ui.imagenesPushButton,
					SIGNAL('clicked(bool)'),
					self.__slotSwitchVerImagenes
					)
		
		# acciones para cambiar el tab
		self.connect(
					self.__ui.tabWebViews,
					SIGNAL('currentChanged(int)'),
					self.__slot_change_tab
					)
		
		
		# acciones para ir a la página principal
		self.connect(
					self.__ui.homeButton,
					SIGNAL('clicked()'),
					self.__slot_goto_home
					)
		
		# acciones para recargar el tab
		self.connect(
					self.__ui.refrescarButton,
					SIGNAL('clicked()'),
					self.__slot_refresh
					)
		
		# acciones para ir atrás
		self.connect(
					self.__ui.atrasButton,
					SIGNAL('clicked()'),
					self.__slot_back
					)
		
		# acciones para ir adelante
		self.connect(
					self.__ui.adelanteButton,
					SIGNAL('clicked()'),
					self.__slot_forward
					)
		
		# acciones para ir adelante
		self.connect(
					self.__ui.pararButton,
					SIGNAL('clicked()'),
					self.__slot_stop
					)
		
		# accion para agregar un nuevo tab
		self.connect(
					self.__ui.actionNuevaPestana,
					SIGNAL('triggered()'),
					self.__slot_new_tab
					)
		self.addAction(self.__ui.actionNuevaPestana)


						
	def create_webkitbrowser(self, context, show_images, _):
		with self.__browser_create_lock:
			if self.__initial_tab_used:
				new_tab = BrowserTab(self, context, show_images)
				close_button = CloseButton(self, new_tab)
				idx = self.__ui.tabWebViews.addTab(new_tab, TabIcon(),
												new_tab.title)
				self.__ui.tabWebViews.tabBar().setTabButton(
														idx,
														QTabBar.RightSide,
														close_button
														)
				return new_tab.browser
			else:
				
				self.__initial_tab_used = True
				return self.__initial_tab.browser
			
		
	def __slotCargarURL(self):
		"Carga la url de la barra de dirección"
		text = self.__ui.direccionlineEdit.text()
		self.__current_webview().setUrl(UrlHelper.from_user_input(text))
		
	def __update_title(self, titulo, idx = None, update_window_title = True):
		"Pone el título correcto en la ventana del browser"
		
		if update_window_title:
			if titulo == None or titulo == '':
				tituloFinal = 'Navegador SDF %s' % Properties.version()
			else:
				tituloFinal = titulo + ' - Navegador SDF %s' % Properties.version() 
			self.setWindowTitle(tituloFinal)
		
		if idx == None:
			idx = self.__ui.tabWebViews.currentIndex()
		self.__ui.tabWebViews.setTabToolTip(idx, titulo)
			
		if not titulo:
			titulo = '(Vacía)'
		if len(titulo) >= 20:
			titulo = titulo[0:20] + '...'
		
		self.__ui.tabWebViews.setTabText(idx, titulo)
		
	def __current_browser(self):
		"Da el browser de la pestaña actual"
		return self.__ui.tabWebViews.currentWidget().browser
	
	def __current_webview(self):
		"Da el webView de la pestaña actual"
		return self.__ui.tabWebViews.currentWidget().webview
	
	def __slot_change_tab(self, tab_num):
		"Cambia el tab"
		current_tab = self.__ui.tabWebViews.widget(tab_num)
		
		self.__update_title(current_tab.title, tab_num, True)
		self.__ui.direccionlineEdit.setText(current_tab.urlbar)		 
		self.__ui.imagenesPushButton.setChecked(current_tab.show_images)
	
		self.__replace_actions(current_tab)
				
	def __slot_goto_home(self):
		"Hace que el browser actual vaya a la página principal"
		home_url = QUrl("http://www.google.com.uy/")
		self.__current_webview().setUrl(home_url)
	
	def __slot_refresh(self):
		self.__current_webview().reload()
	
	def __slotSwitchVerImagenes(self, verImagenes):
		"Maneja el evento de mostrar o no imágenes"
		self.__ui.tabWebViews.currentWidget().set_show_images(verImagenes)
		
	def title_changed(self, browsertab, title, change_window_title):
		"Se llama cuando un browser cambia su título"
		update_title = browsertab == self.__ui.tabWebViews.currentWidget()
		idx = self.__ui.tabWebViews.indexOf(browsertab)
		
		self.__update_title(title, idx, update_title and change_window_title)
		
	def url_changed(self, browsertab, url):
		"Se llama cuando un browser cambia su url"
		if browsertab == self.__ui.tabWebViews.currentWidget():
			self.__ui.direccionlineEdit.setText(url.toString())
			
	def statusbar_changed(self, browsertab, msg):
		"Se llama cuando un browser cambia su barra de estado"
		if browsertab == self.__ui.tabWebViews.currentWidget():
			if type(msg) != QString: # convierte msg a QString
				msg = QString.fromUtf8(msg)
			self.__ui.statusbar.showMessage(msg)

	def __slot_locationbar_changed(self, text):
		"Cuando cambia el contenido de la barra de direcciones"
		self.__ui.tabWebViews.currentWidget().urlbar = text
	
	def tab_closed(self, browsertab):
		"Se llama  cuando se cierra un tab"
		idx = self.__ui.tabWebViews.indexOf(browsertab)
		self.__ui.tabWebViews.removeTab(idx)
	
	def __slot_back(self):
		"Va una página atrás"
		self.__current_webview().back()
		
	def __slot_forward(self):
		"Va una página adelante"
		self.__current_webview().forward()
		
	def __slot_stop(self):
		"Para la carga"
		self.__current_webview().stop()
		
	def __slot_new_tab(self):
		"Agrega un nuevo tab"
		self.create_webkitbrowser(self.__context, True, True)
		new_tab_idx =  self.__ui.tabWebViews.count() - 1
		self.__ui.tabWebViews.setCurrentIndex(new_tab_idx)
	
	def __replace_actions(self, browsertab):
		"""
		Saca las acciones del browser y las reemplaza por las acciones
		de otro tab
		"""
		self.removeAction(self.__refresh_action)
		self.removeAction(self.__back_action)
		self.removeAction(self.__forward_action)

		action = browsertab.webview.page().action(QWebPage.Reload)
		action.setShortcut(QKeySequence.Refresh)
		self.addAction(action) # lo agrega a las acciones de la ventana
		self.__refresh_action = action
			
		action = browsertab.webview.page().action(QWebPage.Back)
		action.setShortcut(QKeySequence.Back)
		self.addAction(action) # lo agrega a las acciones de la ventana
		self.__back_action = action

		action = browsertab.webview.page().action(QWebPage.Forward)
		action.setShortcut(QKeySequence.Forward)
		self.addAction(action) # lo agrega a las acciones de la ventana
		self.__forward_action = action
		
	