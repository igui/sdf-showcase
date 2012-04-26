'''
Created on 30/03/2010

@author: iavas
'''
from sdf import ListBasedParser
from sdf import Driver
import sdf.data
from sdf.postactions.mail_sender import MailSender

class Item(sdf.data.Item):
	def __init__(self, url, n):
		sdf.data.Item.__init__(self, url)
		self.n = n

class Parser(ListBasedParser):
	def __init__(self, context):
		ListBasedParser.__init__(self, context)
	
	def make_paging(self, context):
		"Hace el paginado"
		n = 1
		
		context.postactions.add_postaction(mail_sender)
		
		return [ Item('about:blank', i) for i in range(n) ] 
	
	def process_item(self, context, item):
		"Procesa un item"
		pass
	
	def finalize(self, context, processed_items, unprocessed_items):
		"Se llama luego de procesar los items"
		print(10, processed_items[10].n)
		print(0, processed_items[ 0].n)
		print(-1, processed_items[-1].n)
		print("[-2:-1]")
		for i in processed_items[-2:-1]:
			print(i.n)
		print("[-2:]")
		for i in processed_items[-2:]:
			print(i.n)
		print("[:2]")
		for i in processed_items[:2]:
			print(i.n) 
		
		print("DOONE!")
		
	def get_paralel_num(self):
		return 1

if __name__ == "__main__":
	args = "-p Parser -o test.xml"
	Driver().execute(args)