# *- encoding: utf-8 -*

'''
Created on 21/08/2009

@author: iavas
'''
class Source(object):
	"""
	Contiene la información de una fuente de información, una fuente es un
	sitio web que contiene varias páginas de items a parsear. 
	"""
	
	def __init__(self, url, country = '<unknown>', category = 'None', *args,
				**kwargs):
		self.url = url
		self.country = country
		self.category = category
		for k, v in list(kwargs.items()):
			self.__setattr__(k, v)