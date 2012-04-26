# *- encoding: utf-8 -*
'''
Created on 30/03/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
from sdf import Context
import traceback
from types import NoneType
import sys

class BaseParser(object):
	'''
	Clase base para todos los parsers
	'''
	
	def __init__(self, context):
		check_if_any_type(context, Context)
		self.__context = context
		

	def run(self):
		"Método base para correr el parser"
		res = 1
		try:
			res = self._run()
			
			check_if_any_type(res, [int, int, bool, NoneType])
			if res == None:
				res = 0
			else:
				res = int(res)
		except:
			traceback.print_exc()
			res = 1
		finally:
			self.__context.logger.mark_end()
			
			l_postactions = len(self.__context.postactions.postactions) 
			if l_postactions > 0:
				for i, p in enumerate(self.__context.postactions.postactions):
					self.log("Corriendo postaction %s %d/%d" % (
						p.get_name(), i+1, l_postactions))
					
					try:
						p.run(self.__context, res)
					except:
						print("Error al correr postaction", file=sys.stderr)
						traceback.print_exc()
						
				self.log("Parser terminado")
			
		return res

	def _run(self):
		raise NotImplemented

	def log(self, message, level= None):
		"Loguea en el logger estándar"
		return self.__context.logger.log(message, level)
	