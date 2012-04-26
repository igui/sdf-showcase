# *- encoding: utf-8 -*
'''
Created on 03/12/2010

@author: iavas
'''

class PostAction(object):
	'''
	Clase base para las postactions. Se inicializa con los parámetros
	processed_items que tiene la lista de items procesados, unprocessed_items
	que tiene la lista de items no procesados. 
	El parámetro result que vale True si el parseo anduvo correctamente y
	False si no dio errores.
	'''

	def __init__(self):
		pass
	
	def get_name(self):
		"Da el nombre de la postaction, por defecto es el nombre de la clase"
		return self.__class__.__name__

	def run(self, context, result):
		"""
		Se corre para implementar una postaction. El parámetro context tiene
		el contexto para correr el parser. 	Result es 0 si el parseo 
		finalizó correctamente y 1 si no lo hizo 
		"""
		raise NotImplementedError
		