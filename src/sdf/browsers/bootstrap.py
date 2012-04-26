#!/usr/bin/python
# *- encoding: utf-8 .*
__author__="igui"
__date__ ="$09/04/2009 07:05:31 PM$"

import sys
from threading import Thread, Semaphore
import traceback
import signal
from sdf import Properties
import os
import ctypes
from os import path

class BootstrapEventHandler(object):
	"Manejador de eventos para el bootstrap"
	def handle_error(self, ex):
		"""
		Se llama cuando hubo un error en el programa. Tiene que retornar
		1 si se sale del programa o 0 si no se sale del programa
		""" 
		raise NotImplemented
	
	def on_end(self, res):
		"""
		Se llama al finalizar el programa. Debe llamar a app.exit() y exit()
		para salir
		"""
		raise NotImplemented 

class _DefaultHandler(BootstrapEventHandler):
	"Manejador de eventos usado por defecto"
	def handle_error(self, ex):
		traceback.print_exc()
	
	def __kill(self, pid):
		"""Funcion kill con soporte para Linux y en Win32"""
		if os.name is 'posix':
			# *NIX
			os.kill(pid, signal.SIGTERM)
		else:
			# WIN32
			kernel32 = ctypes.windll.kernel32
			handle = kernel32.OpenProcess(1, 0, pid)
			return (0 != kernel32.TerminateProcess(handle, 0))
	
	def on_end(self, res):
		if res != 1: # Si se retorna algo nulo (None, 0, etc.) sale del programa
			self.__kill(os.getpid())


class BootStrap(object):
	
	# el semáforo para iniciar qt o xulrunner
	__framework_init_sem = Semaphore(0)
	# que framework se va a iniciar "mozilla" para xulrunner y "qt" para qt
	__init_framework = None
	
	@classmethod
	def init_qt(cls):
		"Indica que se va a iniciar qt"
		cls.__init_framework = "qt"
		cls.__framework_init_sem.release()
		
	@classmethod
	def init_mozilla(cls):
		"Indica que se va a iniciar Mozilla (XulRunner)"
		cls.__init_framework = "mozilla"
		cls.__framework_init_sem.release()
	
	@classmethod
	def __init_qt_loop(cls):
		from PyQt4 import QtGui
		
		app = QtGui.QApplication(sys.argv)
			
		# setea cierta información de la aplicación para que funcione guardar settings
		app.setOrganizationDomain(Properties.organization_domain())
		app.setOrganizationName(Properties.organization_name())
		app.setApplicationName(Properties.application_name())
		app.setApplicationVersion(Properties.version())
		
		app.exec_()
		
	@classmethod
	def __init_mozilla_loop(cls):
		from sdf.browsers import mozillabrowser
		from jpype import startJVM, JPackage
		import gtk

		mozillabrowser_path = mozillabrowser.__path__[0]
		app_path = path.join(mozillabrowser_path, "xul_runner_app")
		java_proyect_path = path.join(mozillabrowser_path, "java_embed") 
		
		xulrunner_path = "/home/igui/xulrunner"
		jvm_library = "/usr/lib/jvm/java-6-openjdk/jre/lib/amd64/server/libjvm.so"
		
		java_class_path = [ 
				path.join(java_proyect_path, "bin"),
				path.join(java_proyect_path, "lib", "MozillaGlue.jar"),
				path.join(java_proyect_path, "lib", "MozillaInterfaces.jar")
		]
		
		startJVM(jvm_library, "-Djava.class.path=" + ":".join(java_class_path))
		
		JPackage('embed').BrowserEmbed.run(app_path, xulrunner_path)
	
	@classmethod
	def __wait_for_framework_init(cls):
		"Espera a iniciar el framework de Qt"
		cls.__framework_init_sem.acquire()
		
		if cls.__init_framework == 'qt':
			cls.__init_qt_loop()
		elif cls.__init_framework == 'mozilla':
			cls.__init_mozilla_loop()
			
	
	@classmethod
	def init_and_work(cls, mainFunction, event_handler = None):
		"""
		Inicia las estructuras para hacer el trabajo.
		Se crea un hilo secundario que ejecuta el MainFunction con la función del
		usuario mientras que el hilo principal ejecuta una aplicación Qt.
		
		Se usa event_handler para sobreescribir el manejo de eventos globales en el
		la función del hilo secundario (excepciones y en caso de salida)
		"""
		
		def work(mainFunction, event_handler):
			"La función del hilo secundario"
			res = 1
			try:
				res = mainFunction()
			except Exception as ex: # Maneja las excepciones no manejadas
				res = event_handler.handle_error(ex)
			finally:
				event_handler.on_end(res)
		
		if event_handler == None:
			event_handler = _DefaultHandler()

		# setea el manejador de SIGINT
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		
		# llama al hilo para empezar a correr
		worker = Thread(target = work, args = (mainFunction, event_handler))
		worker.name = "UserMainThread"
		worker.start()

		cls.__wait_for_framework_init()