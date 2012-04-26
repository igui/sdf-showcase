# *- encoding: utf-8 -*
'''
Created on 30/07/2010

@author: iavas
'''
from sdf import PageParser
from sdf import Driver
from sdf.data import Item
from examples.metacafe.data import Options


class Parser(PageParser):
	def __init__(self, context):
		PageParser.__init__(self, context)
			
	def start(self, context):
		"Hace el paginado"
		context.add_page(
			'http://www.metacafe.com/videos/art_and_animation/week',
			parse = self.parse_page
		)
#		context.add_page(
#			'http://www.metacafe.com/videos/comedy/week',
#			parse = self.parse_page
#		)
		
	def parse_page(self, context):
		"Parsea la página"
		
		browser = context.browser
		print("Parsing page '%s'" % context.page.url) 
		
		# agrega los items de la página
		for a in browser.find_many(css = 'p.ItemTitle a.Strong'):
			context.add_page(a.href, parse = self.parse_item)

		# busca si hay una página más para agregar
		next_page_a = browser.find(
								tag = 'a',
								attribute = { 'title' : 'Browse to next page' }
								)
		
		if next_page_a != None and next_page_a.href[-10:] != browser.url[-10:]:
			context.add_page(
							next_page_a.href,
							end_on_error = False,
							parse = self.parse_page
							)



	def parse_item(self, context):
		"Parsea el item"
		browser = context.browser
		
		print("Parsing item '%s'" % context.page.url) 
		
		item = Item(browser.url)
		item.name =  browser.find(id = 'ItemTitle').get_inner_text().strip()
		item.description =  browser.find(id = 'Desc').get_inner_text()
		
		metadata =  browser.find(id = 'MetaData').find_many(tag = 'li')[1].get_html()
		
		item.views  =  context.string_helper.extract(
								"<strong>Views:</strong> # |",
								metadata
								).strip()
		item.rating =  context.string_helper.extract(
								"<strong>Average Rating:</strong> # |",
								metadata
								).strip()
		item.added  =  context.string_helper.extract(
								"Added:</strong> # ",
								metadata
								).strip()
		
		# agrega el ítem procesado
		context.add_item(item)
			
	
	def finalize(self, context, processed_items, unprocessed_items):
		"Se llama al finalizar el proceso"
		context.data_adapter.write_items(processed_items)


	def get_paralel_num(self):
		"La cantidad de browsers a usar cuando se procesan las páginas"
		return 1

if __name__ == "__main__":
	args = "-p Parser"	
	Driver().execute(args, options = Options())
