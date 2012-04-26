# *- encoding: utf-8 -*
'''
Created on 19/02/2010

@author: iavas
'''

from sdf import SimpleParser
from sdf import Driver

class Parser(SimpleParser):
	def __init__(self, context):
		SimpleParser.__init__(self, context)
	
	def parse(self):
		browser = self.browser

		#
		#	Va a una página y empieza a hacer acciones que deberían gastar memoria
		#	Es mejor correr con el monitor de sistema abierto para analizar el 
		#	uso de memoria
		#
		loops = 500
		total_elements = []
		for i in range(0, loops):
			print("loop %d/%d" % (i+1, loops))
			browser.load_page("http://localhost/")
			new_elements = browser.find_many()
			print("Obtenidos %d elementos en la página" % len(new_elements))
			#total_elements += new_elements
			
		print(len(total_elements))
		
		print("DOONE!")

if __name__ == "__main__":
	args = [ "-p", "test.test_memleak.Parser",
			 "-u", "../../config/countries.info",
			 "-W",
			 #"--wk-remain-open" 
			]	
	Driver().execute(args)
