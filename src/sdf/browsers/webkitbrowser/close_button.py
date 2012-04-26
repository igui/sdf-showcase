# *- encoding: utf-8 -*
'''
Created on 11/08/2010

@author: iavas
'''
from PyQt4.QtGui import QPushButton, QPixmap, QIcon
from PyQt4.QtCore import QRect, QSize, SIGNAL


class CloseButton(QPushButton):
	'''
	Representa un botón de cerrar en un tab del browser
	'''

	def __init__(self, parent, browser_tab):
		QPushButton.__init__(self, parent)
		
		# setea el botón de cerrar
		self.setGeometry(QRect(0, 0, 22, 22))
		icon = QIcon()
		icon.addPixmap(
					QPixmap(":/icons/dialog-close.png"),
					QIcon.Normal,
					QIcon.Off
					)
		self.setIcon(icon)
		self.setIconSize(QSize(16, 16))
		self.setFlat(True)
		
		self.connect(self, SIGNAL('clicked()'), self.close)
		self.__parent = parent
		self.__browser_tab = browser_tab
	
	def close(self):
		"Se llama cuando se cierra el browser"
		self.__parent.tab_closed(self.__browser_tab)
		