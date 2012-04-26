'''
Created on 31/03/2010

@author: iavas
'''
import sdf.data

class Item(sdf.data.Item):
	'''
	Item de btjunkie, describe un torrent
	'''


	def __init__(self, url):
		'''
		Constructor
		'''
		sdf.data.Item.__init__(self, url)
		
		self.name = None
		self.category = None
		self.size = None
		self.seeds = None
		self.leech = None
		self.files = None
		
	def __str__(self):
		return ("Item:\nurl -> %s\nname -> %s\ncategory -> %s\nsize -> %s\n" +\
			"\nseeds -> %s\nleech -> %s\nfiles -> %s") % (
				self.url, self.name, self.category, self.size, self.seeds,
				self.leech, self.files)
										 