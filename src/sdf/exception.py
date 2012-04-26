#*- encoding: utf-8 -* 

'''
Created on 08/07/2009

@author: Ignacio
'''

class LogicError(Exception):
	'''
	Expresa un error lógico
	'''

	def __init__(self, msg):
		'''
		Construye un error lógico
		
		msg -- el mensaje del error
		'''
		Exception.__init__(self)
		self.msg = msg 

	def __str__(self):
		return self.msg
	
	
class JavaScriptError(Exception):
	"Un error en javascript"
	
	def __init__(self, msg):
		'''
		Construye un error de javascript
		
		msg -- el mensaje del error
		'''
		Exception.__init__(self)
		self.msg = msg 

	def __str__(self):
		return self.msg
	
class OldElementError(Exception):
	"""
	Representa un error cuando se accede a un elemento que ya no se encuentra
	en el browser
	"""
	def __init__(self, msg):
		'''
		Construye un error
		
		msg -- el mensaje del error
		'''
		Exception.__init__(self)
		self.msg = msg 

	def __str__(self):
		return self.msg
  	

class LoadPageError(Exception):
	"Un error en browser.load_page()"
	
	def __init__(self, msg, code = None, code_msg = None):
		'''
		Construye un error
		
		msg -- el mensaje del error
		'''
		Exception.__init__(self)
		self.msg = msg
		self.code = code
		self.code_msg = code_msg

	def __str__(self):
		return self.msg
