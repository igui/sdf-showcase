#! *- encoding: utf-8 -*

'''
Created on 16/05/2010

@author: amartinez
'''
from sdf import ListBasedParser
from sdf import Driver
from examples.booking.data import Item
from examples.booking.data import Options

from time import sleep

#  -- CONSTANTES --

# Tipos de hoteles
TIPO_APARTAMENTO	= "Apartamento"
TIPO_HOSTAL			= "Hostal"
TIPO_ALBERGUE		= "Albergue"
TIPO_HOTEL			= "Hotel"
TIPO_VILLABUNGALOW	= "VillaBungalow"

# Ciudades y paises
CIUDAD_BARCELONA	= "Barcelona"
PAIS_ES				= "España"
CIUDAD_LONDRES		= "Londres"
PAIS_UK				= "Reino Unido"
CIUDAD_PARIS		= "París"
PAIS_FR				= "Francia"

# Constructores de URLs
URL_FECHA_IDIOMA		= ";checkin_monthday=10;checkin_year_month=2010-6;checkout_monthday=15;checkout_year_month=2010-6;lang=es"
URL_CANT_FILAS_PAG		= "&rows=35"
URL_ID_APT				= "&ht_id=2"
URL_ID_HOSTAL			= "&ht_id=3"
URL_ID_ALBERGUE			= "&ht_id=13"
URL_ID_HOTEL			= "&ht_id=14"
URL_ID_VILLABUNGALOW	= "&ht_id=23"

# URLs
URL_BASE_BARCELONA	= "http://www.booking.com/searchresults.html?lang=es&city=-372490"
URL_BASE_PARIS		= "http://www.booking.com/searchresults.html?lang=es&city=-1456928"
URL_BASE_LONDRES	= "http://www.booking.com/searchresults.html?lang=es&city=-2601889"


class ASimpleParser(ListBasedParser):
	def __init__(self, context):
		ListBasedParser.__init__(self, context)
	
	
	def parse_category(self, context, url_categoria, tipo, ciudad, pais):
		print('Procesando categoria: ' + pais.encode("ascii","ignore") + ' - ' + ciudad.encode("ascii","ignore") + ' - ' + tipo)
		
		# Obtengo el browser.
		browser = context.browser
		
		# Primero proceso hoteles de tipo Apartamento
		browser.load_page(url_categoria)
		
		lista_items = []
		
		# pseudo-repeat en Python...
		while True:
			# Guardo los links a las paginas de hoteles
			links_hoteles = browser.find_many(xpath = "/html/body/div/div/div[5]/table/tbody/tr/td[2]/table/tbody/tr")
			for link in links_hoteles:
				url_hotel = link.find(xpath = "td[2]/h3/a")
				if url_hotel is not None:
					url_hotel_final = url_hotel.href + URL_FECHA_IDIOMA
					hotel = Item(url_hotel_final)
					hotel.tipo = tipo
					hotel.ciudad = ciudad
					hotel.pais = pais
					lista_items.append(hotel)
			
			next = browser.find(xpath = "//table[@class='prevnextbar']//td[@class='next']/a")
			
			if next is None:
				break
			next.click(True)
		
		print('Procesada categoria: ' + pais.encode("ascii","ignore") + ' - ' + ciudad.encode("ascii","ignore") + ' - ' + tipo)
		print('Obtenidos ' + str(len(lista_items)) + ' hoteles.')
		print('-------------------------------------------------------------')
		
		return lista_items
	
	
	def make_paging(self, context):
		"Hace el paginado"
		
		# Obtengo el browser.
		browser = context.browser
		
		# Declaro la lista de items.
		items_hoteles = []
		
		# ------- BARCELONA -------
		# Proceso hoteles de tipo Apartamento
		url = URL_BASE_BARCELONA + URL_ID_APT + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_APARTAMENTO, CIUDAD_BARCELONA, PAIS_ES)
		
		# Proceso hoteles de tipo Hostal
		url = URL_BASE_BARCELONA + URL_ID_HOSTAL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOSTAL, CIUDAD_BARCELONA, PAIS_ES)
		
		# Proceso hoteles de tipo Albergue
		url = URL_BASE_BARCELONA + URL_ID_ALBERGUE + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_ALBERGUE, CIUDAD_BARCELONA, PAIS_ES)
		
		# Proceso hoteles de tipo Hotel
		url = URL_BASE_BARCELONA + URL_ID_HOTEL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOTEL, CIUDAD_BARCELONA, PAIS_ES)
		
		# Proceso hoteles de tipo Villa/Bungalow
		url = URL_BASE_BARCELONA + URL_ID_VILLABUNGALOW + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_VILLABUNGALOW, CIUDAD_BARCELONA, PAIS_ES)
		
		# ------- LONDRES -------
		# Proceso hoteles de tipo Apartamento
		url = URL_BASE_LONDRES + URL_ID_APT + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_APARTAMENTO, CIUDAD_LONDRES, PAIS_UK)
		
		# Proceso hoteles de tipo Hostal
		url = URL_BASE_LONDRES + URL_ID_HOSTAL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOSTAL, CIUDAD_LONDRES, PAIS_UK)
		
		# Proceso hoteles de tipo Albergue
		url = URL_BASE_LONDRES + URL_ID_ALBERGUE + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_ALBERGUE, CIUDAD_LONDRES, PAIS_UK)
		
		# Proceso hoteles de tipo Hotel
		url = URL_BASE_LONDRES + URL_ID_HOTEL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOTEL, CIUDAD_LONDRES, PAIS_UK)
		
		# Proceso hoteles de tipo Villa/Bungalow
		url = URL_BASE_LONDRES + URL_ID_VILLABUNGALOW + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_VILLABUNGALOW, CIUDAD_LONDRES, PAIS_UK)
		
		# ------- PARIS -------
		# Proceso hoteles de tipo Apartamento
		url = URL_BASE_PARIS + URL_ID_APT + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_APARTAMENTO, CIUDAD_PARIS, PAIS_FR)
		
		# Proceso hoteles de tipo Hostal
		url = URL_BASE_PARIS + URL_ID_HOSTAL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOSTAL, CIUDAD_PARIS, PAIS_FR)
		
		# Proceso hoteles de tipo Albergue
		url = URL_BASE_PARIS + URL_ID_ALBERGUE + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_ALBERGUE, CIUDAD_PARIS, PAIS_FR)
		
		# Proceso hoteles de tipo Hotel
		url = URL_BASE_PARIS + URL_ID_HOTEL + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_HOTEL, CIUDAD_PARIS, PAIS_FR)
		
		# Proceso hoteles de tipo Villa/Bungalow
		url = URL_BASE_PARIS + URL_ID_VILLABUNGALOW + URL_CANT_FILAS_PAG
		items_hoteles += self.parse_category(context, url, TIPO_VILLABUNGALOW, CIUDAD_PARIS, PAIS_FR)
		
		print('******************************************')
		print('Paginado finalizado...')
		print('Obtenidos ' + str(len(items_hoteles)) + ' hoteles.')
		print('******************************************')
				
		return items_hoteles
			
			
	def process_item(self, context, item):
		"Procesa un item"
		browser = context.browser
		
		print('procesando url: ' + browser.url)
		
		# Obtengo el nombre del hotel.
		elem_nombre = browser.find(xpath = "//table[@id='basiclayout']/tbody/tr/td[2]/h1")
		if elem_nombre is None:
			print('ERROR -- Hotel sin nombre... Url: ' + browser.url)
			return
		item.nombre = elem_nombre.innerText.strip()
		
		# Obtengo cantidad de estrellas.
		elem_estrellas = browser.find(xpath = "//table[@id='basiclayout']/tbody/tr/td[2]/h1//img")
		if elem_estrellas is not None:
			item.estrellas = elem_estrellas.title[0] # TODO: revisar....		
		else:
			item.estrellas = 'null'
			#print 'Hotel sin nombre... Url: ' + browser.url
			#return
			
		# Obtengo calificacion promedio.
		elem_calif = browser.find(xpath = "//p[@class='rating']//span[@class='average']")
		if elem_calif is not None:
			item.calif_promedio = elem_calif.innerText
		else:
			item.calif_promedio = 'null'
			#print 'Hotel sin nombre... Url: ' + browser.url
			#return
			
		# Obtengo la direccion.
		elem_dir = browser.find(xpath = "//table[@id='basiclayout']/tbody/tr/td[2]/p")
		if elem_dir is None:
			print('ERROR -- Hotel sin direccion... url: ' + browser.url)
			return
		item.direccion = context.string_helper.extract("# (Mostrar", elem_dir.innerText)
		
		# Obtengo cantidad de habitaciones y cadena (si corresponde).
		div_content = browser.find(xpath = "//div[@id='hotel_main_content']/p[@class='summary']")
		if div_content is None:
			print('ERROR -- Hotel sin contenido (c_hab, cadena)... url: ' + browser.url)
			return
		# Cantidad de habitaciones
		item.cant_hab = context.string_helper.extract("hotel: #.", div_content.innerText)
		# Cadena
		item.cadena = context.string_helper.extract("hotelera: #.", div_content.innerText)
		
		# Extraigo comentarios.
		lista_comentarios = browser.find_many(xpath = "//table[@id='comments_table']/tbody/tr")
		
		for comentario in lista_comentarios:
			dicc_comentarios = {}
		
			nombre = comentario.find(tag = 'div', class_name = 'cell_user_name')
			grupo = comentario.find(tag = 'div', class_name = 'cell_user_profile')
			fecha = comentario.find(tag = 'span', class_name = 'cell_user_date dtreviewed')
			local = comentario.find(tag = 'span', class_name = 'locality')
			pais = comentario.find(tag = 'span', class_name = 'country-name')
			calif = comentario.find(tag = 'td', class_name = 'cell_score')
			com_bueno = comentario.find(tag = 'p', class_name = 'comments_good')
			com_malo = comentario.find(tag = 'p', class_name = 'comments_bad')
			
			if nombre is None:
				# No es un comentario...
				continue
			else:
				dicc_comentarios['nombre'] = nombre.innerText.strip()
			
			if grupo is None:
				dicc_comentarios['grupo'] = 'null'
			else:
				dicc_comentarios['grupo'] = grupo.innerText.strip()
				
			if fecha is None:
				dicc_comentarios['fecha'] = 'null'
			else:
				dicc_comentarios['fecha'] = fecha.innerText.strip()
				
			if local is None:
				dicc_comentarios['local'] = 'null'
			else:
				dicc_comentarios['local'] = local.innerText.strip()
				
			if pais is None:
				dicc_comentarios['pais'] = 'null'
			else:
				dicc_comentarios['pais'] = pais.innerText.strip()
				
			if calif is None:
				dicc_comentarios['calif'] = 'null'
			else:
				dicc_comentarios['calif'] = calif.innerText.strip()
				
			if com_bueno is None:
				dicc_comentarios['com_bueno'] = 'null'
			else:
				dicc_comentarios['com_bueno'] = com_bueno.innerText.strip()
				
			if com_malo is None:
				dicc_comentarios['com_malo'] = 'null'
			else:
				dicc_comentarios['com_malo'] = com_malo.innerText.strip()
			
			
			item.comentarios.append(dicc_comentarios)
		
		# Lista de habitaciones disponibles.
		lista_hab = browser.find_many(xpath = "//table[@id='maxotel_rooms']/tbody/tr")
		
		for hab in lista_hab:
			dicc_habs = {}
			hab_tipo = hab.find(tag = 'a', class_name = 'togglelink jqrt')
			if hab_tipo is None:
				# Este elemento no es una habitacion...
				continue
			dicc_habs['tipo'] = hab_tipo.innerText.strip()
			
			hab_precio_td = hab.find(tag = 'td', class_name = 'roomPrice figure')
			if hab_precio_td is None:
				dicc_habs['precio'] = 'null'
			else:
				hab_precio = hab_precio_td.find(tag = 'div', class_name = 'roomDefaultUse')
				if hab_precio is None:
					dicc_habs['precio'] = 'null'
				else:
					precios = hab_precio.innerText.encode("ascii","ignore").strip().partition(" ")
					# precios = [PRIMER PRECIO, " ", SEGUNDO PRECIO] O # precios = [PRIMER PRECIO, "", ""]
					if precios[2] is not "":
						dicc_habs['precio'] = precios[2]
					else:
						dicc_habs['precio'] = precios[0]
			
			# cantidad disponible
			disponibles_select = hab.find(tag = 'select', class_name = 'b_available_multi_room_price')
			if disponibles_select is not None:
				dicc_habs['cantidad'] = str( len(disponibles_select.find_many(tag = "option")) - 1 )
			else:
				dicc_habs['cantidad'] = '0'			
			
			item.habitaciones.append(dicc_habs)
			
		return
	
	def finalize(self, context, processed_items, unprocessed_items):
		"Se llama luego de procesar los items"
		context.data_adapter.write_items(processed_items)
	
	def get_paralel_num(self):
		return 1
	
	def get_process_item_browser_type(self):
		#return self.browser_type.BasicBrowser
		return self.browser_type.WebKitBrowser
	
	def get_paging_browser_type(self):
		#return self.browser_type.BasicBrowser
		return self.browser_type.WebKitBrowser

if __name__ == "__main__":
	args = [ "-p", "ASimpleParser",
			 "-u", "../../config/countries.info", 
			 #"-W",
			 "--wk-remain-open",
			 "-d",
			 #"-c",
			 #"-f",
			 "--wk-hide-images"			 
			 ]	
	Driver().execute(args, options = Options())
