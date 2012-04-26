'''
Created on 28/04/2010

@author: iavas
'''

class ParserLoader(object):
	"Modela una clase que sirve para cargar un parser a partir de las opciones"
	
	def get_parser_class(self, options):
		"Carga la clase del parser y la devuelve"
		raise NotImplementedError
	
	def parser_loaded(self, context, parser):
		"Se llama cuando se carga el parser"
		pass