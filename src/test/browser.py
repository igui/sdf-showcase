# *- encoding: utf-8 -*
'''
Created on 14/09/2009

@author: iavas
'''


from sdf import SimpleParser
from sdf import Driver

class Browser(SimpleParser):
	def __init__(self, context):
		SimpleParser.__init__(self, context)
	
	def parse(self):
		# carga una página
		self.browser.load_page("http://www.google.com")

if __name__ == "__main__":
	args = [ "-p", "Browser",
			 "-W",
			 "--wk-remain-open", 
			]	
	Driver().execute(args)
