# *- encoding: utf-8 -*
'''
Created on 04/06/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
from types import NoneType

class FileLogger(object):
	'''
	Una clase que emula ser un archivo y loguea cada vez que ese escribe en él
	'''

	def __init__(self, logger, encoding, logging_level = None):
		from sdf import Logger
		check_if_any_type(logger, Logger)
		check_if_any_type(logging_level, (NoneType, int, int))
		self.__logger = logger
		self.__pending_line = ""
		
		if logging_level == None:
			logging_level = Logger.MessageLevel.Info
		self.__logging_level = logging_level
		
		self.encoding = encoding
		
		
	def write(self, data):
		data = data.replace("\r\n", "\n")
		
		breaks = []
		for i in range(len(data)): # busca los fines de línea
			if data[i] == '\n':
				breaks.append(i)
		
		if len(breaks) == 0: # no hay fin de línea
			self.__pending_line = self.__pending_line + data		
		else: # hay al menos uno
			# imprime la primera línea
			line = self.__pending_line + data[:breaks[0]]
			self.__logger.log(line,	self.__logging_level)
			
			for i in range(1, len(breaks)): # imprime el resto
				min_index = breaks[i-1] + 1
				max_index = breaks[i]
				msg = data[min_index:max_index]
				self.__logger.log(msg, level = self.__logging_level)
		
			# guarda la cola de lo impreso para imprimir después
			self.__pending_line = data[breaks[-1]+1:]
			
	def flush(self):
		self.__logger.log(str(self.__pending_line))
		self.__pending_line = ""
		