from xml.dom.minidom import Document

class DataAdapterXML(object):
	
	def __init__(self, context):
		self.output_file = context.options.output_file
		doc = Document()
		collection = doc.createElement("HotelesCollection")
		doc.appendChild(collection)
		f=open(self.output_file, 'w')
		doc.writexml(f)

	def __create_text_node(self, tag, value, doc):
		if value is None:
			node = doc.createElement(tag)
			cdata = doc.createCDATASection('null')
			node.appendChild(cdata)
		else:
			node = doc.createElement(tag)
			cdata = doc.createCDATASection(value.encode('utf-8'))
			node.appendChild(cdata)
		return node
	
	def __create_node(self, tag, value, doc):
		if value is None:
			node = doc.createElement(tag)
			text = doc.createTextNode('null')
			node.appendChild(text)
		else:		
			node = doc.createElement(tag)
			text = doc.createTextNode(value.encode('utf-8'))
			node.appendChild(text)
		
		return node
		
	def __write_item(self, item, doc):
		oferta = doc.createElement('hotel')		
		
		temp = self.__create_node('url', item.url, doc)
		oferta.appendChild(temp)

		temp = self.__create_node('nombre', item.nombre, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_node('tipo', item.tipo, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_node('ciudad', item.ciudad, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('pais', item.pais, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('direccion', item.direccion, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('cadena', item.cadena, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('estrellas', item.estrellas, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('califPromedio', item.calif_promedio, doc)
		oferta.appendChild(temp)
		
		temp = self.__create_text_node('cantHab', item.cant_hab, doc)
		oferta.appendChild(temp)		
		
		# Lista de habitaciones.
		habitaciones = doc.createElement('habitaciones_disponibles')
		for hab in item.habitaciones:
			# Claves del diccionario hab: tipo, precio, cantidad
			item_habitacion = doc.createElement('habitacion')
			
			temp = self.__create_text_node('tipo', hab['tipo'], doc)
			item_habitacion.appendChild(temp)
			
			temp = self.__create_text_node('precio', hab['precio'], doc)
			item_habitacion.appendChild(temp)
			
			temp = self.__create_text_node('cantidad', hab['cantidad'], doc)
			item_habitacion.appendChild(temp)
			
			habitaciones.appendChild(item_habitacion)		
		
		oferta.appendChild(habitaciones)
		
		# Lista de comentarios.
		comentarios = doc.createElement('lista_comentarios')
		for com in item.comentarios:
			# Claves del diccionario com: nombre, grupo, fecha, local, pais, calif, com_bueno, com_malo
			item_comentario = doc.createElement('comentario')
			
			temp = self.__create_text_node('nombre', com['nombre'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('grupo', com['grupo'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('fecha', com['fecha'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('localidad', com['local'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('pais', com['pais'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('com_positivo', com['com_bueno'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('com_negativo', com['com_malo'], doc)
			item_comentario.appendChild(temp)
			
			temp = self.__create_text_node('calificacion', com['calif'], doc)
			item_comentario.appendChild(temp)			
			
			comentarios.appendChild(item_comentario)		
		
		oferta.appendChild(comentarios)
		
		return oferta
		
	
	def write_items(self, items):
		doc = Document()
		collection = doc.createElement("HotelesCollection")
		doc.appendChild(collection)
		for item in items :			
			item_node = self.__write_item(item, doc)
			doc.documentElement.appendChild(item_node)
		f=open(self.output_file, 'w')
		doc.writexml(f, encoding='utf-8')
		

		
