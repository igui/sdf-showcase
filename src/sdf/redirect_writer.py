# *- encoding: utf-8 -*
'''
Created on 03/12/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type

class RedirectWriter:
	'''
	Un objeto de "tipo" file que al escribirse, hace que se escriba a otros
	objetos más llamando a sus métodos write. 
	'''
	
	def __init__(self, redirect_dests, encoding):
		check_if_any_type(redirect_dests, list)
		
		self.__redirect_dests = redirect_dests
		self.__encoding = encoding
		
	def write(self, data):
		"Redefinición de los método write"
		for dest in self.__redirect_dests:
			try:
				dest.write(data)
			except:
				dest.write(data.encode('ascii', 'backslashreplace'))
				
	def flush(self):
		for dest in self.__redirect_dests:
			dest.flush()
						
	@property
	def encoding(self):
		return self.__encoding
