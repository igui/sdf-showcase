# *- encoding: utf-8 -*
'''
Created on 25/01/2010

@author: iavas
'''

def synchronized_method(lock_member):
	"""
	Synchronization decorator para un método de una clase
	Parámetros
	lock_member -- el string del miembro de la clase que es el lock	
	"""

	def wrap(f):
		def newFunction(self, *args, **kw):
			lock = self.__getattribute__(lock_member)
			lock.acquire()
			try:
				return f(self, *args, **kw)
			finally:
				lock.release()
		return newFunction
	return wrap