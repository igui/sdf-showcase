# *- encoding: utf-8 -*
'''
Created on 07/09/2009

@author: iavas
'''

class Item(object):
	'''
	Representa un item a parsear, esta debe ser derivada por los parsers
	para representar los items
	'''


	def __init__(self, url):
		'''
		Constructor de item, el parámetro *url* toma la url de la página que
		contiene los datos del item
		'''
		self.url = url 
		