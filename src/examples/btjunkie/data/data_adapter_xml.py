from xml.dom.minidom import Document

class DataAdapterXML(object):
	
	def __init__(self, context):
		self.output_file = context.options.output_file
		doc = Document()
		collection = doc.createElement("TorrentCollection")
		doc.appendChild(collection)
		f=open(self.output_file, 'w')
		doc.writexml(f)

	def __create_text_node(self, tag, value, doc):
		node = doc.createElement(tag)
		cdata = doc.createCDATASection(value.encode('utf-8'))
		node.appendChild(cdata)
		return node
	
	def __create_node(self, tag, value, doc):
		node = doc.createElement(tag)
		text = doc.createTextNode(value.encode('utf-8'))
		node.appendChild(text)
		return node
		
	def __write_item(self, item, doc):
		oferta = doc.createElement('torrent')

		temp = self.__create_node('url', item.url, doc)
		oferta.appendChild(temp)

		temp = self.__create_node('category', item.category, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_node('size', item.size, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_node("seeds", str(item.seeds), doc)
		oferta.appendChild(temp)				
				
		temp = self.__create_node("leech", item.leech, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_node("file_count", item.files, doc)
		oferta.appendChild(temp)
		
		oferta.appendChild(temp)
		
		return oferta
		
	
	def write_items(self, items):
		doc = Document()
		collection = doc.createElement("TorrentCollection")
		doc.appendChild(collection)
		for item in items :			
			item_node = self.__write_item(item, doc)
			doc.documentElement.appendChild(item_node)
		f=open(self.output_file, 'w')
		doc.writexml(f, encoding='utf-8')
		

		