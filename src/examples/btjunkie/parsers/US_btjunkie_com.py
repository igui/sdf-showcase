'''
Created on 31/03/2010

@author: iavas
'''
from sdf import ListBasedParser
from sdf import Driver
from examples.btjunkie.data import Item
from examples.btjunkie.data import Options


class Parser(ListBasedParser):
	def __init__(self, context):
		ListBasedParser.__init__(self, context)
	
	def make_paging(self, context):
		"Hace el paginado"
		browser = context.browser
		
		browser.load_page('http://btjunkie.org/?do=latest')
		return [ 
			Item(h.href) 
			for h in browser.find_many(tag = 'a', class_name = 'BlckUnd')
			]
	
	def process_item(self, context, item):
		"Procesa un item"
		browser = context.browser
		
		item.name =	browser.find(
			tag = 'font',
			attribute = { 'style': 'font-size:14pt' }
			).get_html()
		
		div_info = browser.find_many(
					tag = 'div',
					attribute = { 'style': 'margin: 10px;' }
					)[-1]
		
		item.files = context.string_helper.extract(
				"<b>#file",
				div_info.find_many(tag = 'tr')[0].find(
					class_name = "Grey6Und").get_html()
			).strip()
			
		item.size = context.string_helper.extract(
						"# in",
						div_info.find(text_contains = ' in').get_inner_text()
					)
		
		item.category = context.string_helper.extract( 
			"<b>#</b>",
			div_info.find(tag = 'a',
						class_name='Grey6Und',
						re_test = { 'href' : 'browse' }
				).get_html())
		
		th_seeds = div_info.find_many(
			tag = 'th',
			attribute = { 'width' : '299', 'align' : 'left' }
			)[1]
		
		item.seeds = context.string_helper.extract(
						"<b># seeds",
						th_seeds.get_html()
				)
		item.leech = context.string_helper.extract(
						"| # peers",
						th_seeds.get_html()
				)
	
	def finalize(self, context, processed_items, unprocessed_items):
		"Se llama luego de procesar los items"
		context.data_adapter.write_items(processed_items)
	
	def get_paralel_num(self):
		return 25
	
	def get_process_item_browser_type(self):
		return self.browser_type.BasicBrowser
	
	def get_paging_browser_type(self):
		return self.browser_type.BasicBrowser

if __name__ == "__main__":
	args = "-p Parser"	
	Driver().execute(args, options = Options())