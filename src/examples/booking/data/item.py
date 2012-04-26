'''
Created on 16/05/2010

@author: amartinez
'''
import sdf.data

class Item(sdf.data.Item):
	'''
	Item de booking, describe un hotel
	'''


	def __init__(self, url):
		'''
		Constructor
		'''
		sdf.data.Item.__init__(self, url)
		
		
		self.tipo = None
		self.nombre = None
		self.ciudad = None
		self.pais = None
		self.direccion = None
		self.cant_hab = None
		self.direccion = None
		self.cadena = None
		self.estrellas = None
		self.calif_promedio = None
		
		# Lista de diccionarios. Claves del dicc:
		# nombre, grupo, fecha, local, pais, calif, com_bueno, com_malo
		self.comentarios = []
		
		# Lista de diccionarios. Claves del dicc:
		# tipo, precio, cantidad
		self.habitaciones = []
	
		
	def __str__(self):
		return ("Item:\nurl -> %s\nnombre -> %s\n") % (self.url, self.nombre)
										 
