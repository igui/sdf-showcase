# *- encoding: utf-8 -*
'''
Created on 31/03/2010

@author: iavas
'''
import sdf.data

class Item(sdf.data.Item):
	"Describe un video de metacafe. La url es la de la página web del item"
	
	def __init__(self, url):
		sdf.data.Item.__init__(self, url)
		
		self.name = None
		self.description = None
		self.views = None
		self.rating = None
		self.added = None
			