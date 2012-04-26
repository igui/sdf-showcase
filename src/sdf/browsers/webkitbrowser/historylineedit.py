'''
Created on 10/03/2010

@author: iavas
'''
from PyQt4 import QtGui, QtCore

class HistoryLineEdit(QtGui.QLineEdit):
	'''
	Un line edit que soporta historial
	'''
	def __init__(self, parent = None):
		'''
		Constructor
		'''
		QtGui.QLineEdit.__init__(self)
		
		self.__history = []
		self.__history_pos = 0
		self.__last_text = ""
		
		self.connect(self, QtCore.SIGNAL('returnPressed (void)'), self,
					QtCore.SLOT('__return_pressed_slot(void)'))
		
	def keyPressEvent(self, event):
		"""
		Maneja los eventos de tecleo, para manejar la historia y permitir tabs
		en el line edit
		"""		
		key = event.key()
		if key == QtCore.Qt.Key_Up:
			self.__history_up()
		elif key == QtCore.Qt.Key_Down:
			self.__history_down()
		else:
			return QtGui.QLineEdit.keyPressEvent(self, event)
	
	def __history_down(self):
		if self.__history_pos < len(self.__history) - 1:
			self.__history_pos += 1
			self.setText(self.__history[self.__history_pos])
		elif self.__history_pos == len(self.__history) - 1:
			self.__history_pos += 1
			self.setText(self.__last_text) 
			
	def __history_up(self):
		if self.__history_pos > 0:
			if self.__history_pos == len(self.__history):
				self.__last_text = self.text()
			
			self.__history_pos -= 1
			self.setText(self.__history[self.__history_pos])

	@QtCore.pyqtSignature("void")
	def __return_pressed_slot(self):
		self.__history.append(self.text())
		self.__history_pos = len(self.__history)
