# *- encoding: utf-8 -*
'''
Created on 04/03/2010

@author: iavas
'''
from code import InteractiveInterpreter
from .uiconsole import Ui_ConsoleWidget
from PyQt4 import QtCore
from PyQt4 import QtGui
from sdf.exception import LogicError
import sys
from sdf.util.typecheck import check_if_any_type
from types import NoneType
from sdf.itemprocessorpipeline import ItemProcesorPipeline
from sdf.helpers import DateHelper, \
	EmailHelper, ErrorHelper, PhoneHelper, StringHelper, TextHelper, UrlHelper
from sdf.redirect_writer import RedirectWriter
from sdf.properties import Properties


class _StrangeInteractiveConsole(InteractiveInterpreter):
	'''
	Se encarga de mantener una consola activada y de ejecutar los comandos
	'''
	def __init__(self, console_widget, locals = {}):
	
		self.__console_widget = console_widget
			
		self.__ps1 = ">>> " 
		self.__ps2 = "... "
		self.__ps = self.__ps1
		self.__partial_source = ""
		
		# se encarga de ejecutar los comandos
		self.__command_procesor = ItemProcesorPipeline(1)
		
		self.__locals = self.__init_locals(locals)
		InteractiveInterpreter.__init__(self, locals)

	def help(self):
		"Imprime las variables disponibles en la consola"
		message = """Variables disponibles:
Alias               Descripción
-----               -----------
find                browser.find
find_many           browser.find_many
load_page           browser.load_page
get_basic_browser   Devuelve un basic_browser nuevo

Alias para los helpers:
DateHelper, EmailHelper, ErrorHelper, PhoneHelper, StringHelper, TextHelper, UrlHelper
"""
		self.__console_widget.write(message, color = 'green')
		# -------- Fin Help ---------	

	def __init_locals(self, locals):
		from sdf.browsers import BrowserFactory
		
		if '__name __' not in locals:
			locals['__name__'] = '__browser_console__'
		if '__doc__' not in locals:
			locals['__doc__'] = "Dummy browser console module"
		
		# chequea que pasen bien el webkitbrowser
		if 'browser' not in locals:
			raise LogicError("locals must have a browser variable")
		
		browser = locals['browser']
		
		def get_basic_browser():
			"Devuelve un basic_browser"
			return BrowserFactory.get_instance().get_basicbrowser()
		
		locals['find']				= browser.find
		locals['find_many']			= browser.find_many
		locals['load_page']			= browser.load_page
		locals['get_basic_browser']	= get_basic_browser
				
		locals['DateHelper'] 	= DateHelper
		locals['EmailHelper'] 	= EmailHelper
		locals['ErrorHelper']	= ErrorHelper
		locals['PhoneHelper']	= PhoneHelper
		locals['StringHelper']	= StringHelper
		locals['TextHelper']	= TextHelper
		locals['UrlHelper']		= UrlHelper
		
		help = self.help
		
		locals['help'] 			= self.help
					
		return locals
		
	def write(self, data):
		self.__console_widget.write(data, color = 'red')
	
	def push_command(self, command):
		"Procesa un comando, lo hace en segundo plano"
		self.__command_procesor.push(self.__synchro_push_command, command)
	
	def __synchro_push_command(self, command):
		"""
		Esta función se llama cuando el ItemProcesorPipeline pone a correr
		el comando
		"""
		self.__console_widget.write(self.__ps + command + '\n', color = "blue",
			bold = True)
		
		if self.__partial_source:
			self.__partial_source += "\n" + command
		else:
			self.__partial_source += command
		
		if self.runsource(self.__partial_source, "<browser console>"):
			# faltan más líneas de código
			self.__ps = self.__ps2
		else:
			self.__partial_source = ""
			self.__ps = self.__ps1 

class Console(QtGui.QWidget, Ui_ConsoleWidget):
	"Un widget que emula una consola de python"
	
	__maxLines = 200 # la cantidad máxima de líneas de la consola
	
	def __init__(self, parent, locals):
		QtGui.QWidget.__init__(self, parent)
		Ui_ConsoleWidget.__init__(self)
		
		sys.stdout = RedirectWriter( [sys.stdout, self], sys.stdout.encoding)
		
		self.__console_controller = _StrangeInteractiveConsole(self, locals)

		self.setupUi(self)
		
		self.__console_commandline = self.consoleCommandLine
		self.__console_commandoutput = self.consoleOutputBox
		
		# limita la cantidad de líneas máxima en el output
		self.__console_commandoutput.document().setMaximumBlockCount(
			Console.__maxLines)

		self.connect(self, QtCore.SIGNAL('write_signal(QString, QString, bool)'),
			self, QtCore.SLOT('__write_data_slot(QString, QString, bool)') )
		self.connect(self.__console_commandline, 
					QtCore.SIGNAL('returnPressed(void)'),
					self, QtCore.SLOT('__push_command_slot(void)'))
		
		
		# cambia la fuente del commandoutput y commandline si está en windows
		if sys.platform.find("win") != -1:
			font = QtGui.QFont()
			font.setFamily("Courier New")
			font.setPointSize(9)
			self.__console_commandoutput.setFont(font)
			self.__console_commandline.setFont(font)
		
		banner = """Navegador SDF %s - Intérprete de comandos
Use la variable browser para comunicarse con el navegador.
Para ver otras variables use help()

""" % Properties.version()
		self.write(banner, 'green', True)
		
		self.__console_controller.help()
		
	@QtCore.pyqtSignature("QString, QString, bool")
	def __write_data_slot(self, data, color, bold):
		"Imprime los datos en sí"
		# hace que se scrolee hacia abajo
		self.__console_commandoutput.moveCursor(QtGui.QTextCursor.End,
											QtGui.QTextCursor.MoveAnchor)
		
		if bold:
			self.__console_commandoutput.setFontWeight(QtGui.QFont.Bold)
		else:
			self.__console_commandoutput.setFontWeight(QtGui.QFont.Normal)

		self.__console_commandoutput.setTextColor(QtGui.QColor(color))
		self.__console_commandoutput.insertPlainText(str(data))
		
		# hace que se scrolee hacia abajo
		vertical_scrollbar = self.__console_commandoutput.verticalScrollBar()
		vertical_scrollbar.setValue(vertical_scrollbar.maximum())
		
	def write(self, data, color = None, bold = False):
		"""
		Escribe caracteres en la salida de la consola, le da formato y 
		manda la señal a __write_data_slot para que escriba
		"""
		check_if_any_type(color, [ NoneType, str, str ])
		
		if color == None:
			color = 'black'

		self.emit(QtCore.SIGNAL('write_signal(QString, QString, bool)'),
				str(data), color, bold)
		
	@QtCore.pyqtSignature("void")
	def __push_command_slot(self):
		text = str(self.__console_commandline.text())
		self.__console_commandline.clear()
		self.__console_controller.push_command(text)
