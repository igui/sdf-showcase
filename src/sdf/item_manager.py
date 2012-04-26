# *-coding: utf-8-*
'''
Created on 05/04/2010

@author: iavas
'''
import sqlite3
import os.path
import pickle as pickle
from sdf.util.typecheck import check_if_any_type
from threading import Lock

class DatabaseList(object):
	'''
	Clase que emula un contenedor utilizando un cursor para iterar sobre items
	en una base de datos.
	'''

	def __init__(self, yield_func, conn_factory, sql_items, count_sql):
		check_if_any_type(conn_factory, _ConnFactory)
		check_if_any_type(sql_items, str)
		check_if_any_type(count_sql, str)
		
		self.__conn_factory = conn_factory
		self.__sql_items = sql_items
		self.__count_sql = count_sql
		self.__yield_func = yield_func
		self.__length = self.__get_length()
		
	def __get_length(self):
		conn = self.__conn_factory.get_connection()
		with conn:
			c = conn.execute(self.__count_sql)
			res = c.fetchone()[0]
			c.close()
			return res
		
	def __iter__(self):
		"Retorna el iterador sobre la lista"
		max_prefetched_rows = 100
		offset = 0
		prefetched_rows = []
		
		while True:
			if len(prefetched_rows) == 0: # no hay más filas
				# saca algunas más 
				prefetched_rows = self.__get_rows(offset, max_prefetched_rows)
				offset += len(prefetched_rows)
				if len(prefetched_rows) == 0: # se terminó la lista
					break
			r = prefetched_rows.pop(0)
			yield self.__yield_func(r['num'], r['processed'], r['serialized'])
			

	def __get_rows(self, offset, max):
		"Obtiene más filas de la base"
		conn = self.__conn_factory.get_connection()
		with conn:
			if max == None: # se da todos los items hasta el final
				max = -1
				
			sql = "%s LIMIT ?,?" % self.__sql_items
			cursor = conn.execute(sql, (offset, max))
			
			res = cursor.fetchall()
			cursor.close()
		return res

	def __normalize_index(self, i):
		"Normaliza el índice y devuelve algo entre 0 y self.__length"
		if i >= self.__length:
				raise IndexError
		elif i < 0:
			i = self.__length + i 
			if i < 0:
				raise IndexError
		return i

	def __get_yielded(self, row):
		"Obtiene el objeto resultado del yield"
		return self.__yield_func(row['num'],row['processed'],row['serialized'])

	def __get_index(self, i):
		"Obtiene una fila solamente"
		i = self.__normalize_index(i)
		
		conn = self.__conn_factory.get_connection()
		with conn:
			sql = "%s LIMIT ?,1" % self.__sql_items
			cursor = conn.execute(sql, (i,))
			r = cursor.fetchone()
			cursor.close()
		
		return self.__get_yielded(r)
	
	def __get_slice(self, key):
		"Da un slice de la lista"
		# obtiene el comienzo 
		if key.start == None:
			offset = 0
		else:
			offset = key.start
		offset = self.__normalize_index(offset)
			
		# obtiene el máximo número de resultados
		if key.stop == None:
			max = None
		else:
			max = key.stop - offset
			max = self.__normalize_index(max)
		
		# obtiene los pasos y si la secuencia va al revés o no
		if key.step == 0:
			raise ValueError("index cannot be zero")
		elif key.step == None:
			step = 1
		else:
			step = key.step
			
		if max <= 0: 
			return []
		else:
			rows = self.__get_rows(offset, max)[::step]
			return [ self.__get_yielded(r) for r in rows ]
		
	
	def __getitem__(self, key):
		"Obtiene un item de la lista"
		if isinstance(key, int):
			return self.__get_index(key)
		elif isinstance(key, slice):
			return self.__get_slice(key)
		else:
			raise TypeError("index must be an integer")
		
	
	def __len__(self):
		"Retorna el largo de la lista"
		return self.__length


class _ConnFactory(object):
	"""
	Se encarga de dar conexiones a una base de datos sqlite3. Toma la ruta
	a la base de datos sqlite en el parámetro db_path
	"""
	
	def __init__(self, db_path):
		self.__db_path = db_path
	
	def get_connection(self):
		connection = sqlite3.connect(self.__db_path)
		connection.text_factory = str
		connection.row_factory = sqlite3.Row
			
		return connection


class ItemManager(object):
	'''
	Una clase que maneja los items de la base de datos
	'''
	def __init__(self, db_path, replace_items):
		"""
		Inicia el item manager
		*db_path*
			Indica la ruta a la base de datos
		*replace_items*
			Si es true, se borra la base de datos y se usa una nueva
		"""
			
		# para matchear la conexión con el hilo actual
		self.__db_path = db_path
		self.__lock = Lock()
		
		if replace_items:
			# si se tiene que empezar con una base de datos nueva, borra el archivo
			if os.path.exists(db_path):
				os.remove(db_path)
			self.__init_db()
		else:
			if not os.path.exists(db_path):
				raise ValueError("Continue last option specified, but '%s' was not found to recover items" % db_path)
			# chequea que exista la base de datos
			self.__check_db()
	
	def __get_connection(self):
		"Da la conexión respectiva a la base de datos"
		return _ConnFactory(self.__db_path).get_connection()
		 
		
	def __check_db(self):
		conn = self.__get_connection()
		
		tables = conn.execute("""
			SELECT		name
			FROM		sqlite_master
		""").fetchall()
		tables = [ t[0] for t in tables ]
		
		expected_tables = ['raw_items', 'log', 'items']
		for t in expected_tables:
			if t not in tables:
				raise LookupError("Database file '%s' doesn't seem to be an parser item database" % (self.__db_path))
		
		conn.close()
		
	def __init_db(self):
		"Inicia las tablas de la base de datos"
		
		conn = self.__get_connection()
			
		conn.execute("""
		CREATE TABLE "raw_items"
		(
			"num" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
			"url" TEXT NOT NULL ,
			"serialized" BLOB NOT NULL ,
			"processed" BOOL NOT NULL 
		)
		""")
		
		conn.execute("""
		CREATE  TABLE "main"."log"
		(
			"date" DATETIME NOT NULL  DEFAULT CURRENT_TIME,
			"item_num" INTEGER NOT NULL ,
			"message" TEXT NOT NULL
		)
		""")
		
		conn.execute("""
		CREATE VIEW items AS
		
		SELECT	i.num as num,
				i.url as url,
				i.serialized as serialized,
				i.processed as processed,
				0 as errors
		FROM raw_items i
		WHERE NOT EXISTS (SELECT * FROM log l WHERE l.item_num = num)

		UNION
		
		SELECT	i.num as num,
				i.url as url,
				i.serialized as serialized,
				i.processed as processed,
				count(*) as errors
		FROM raw_items i, log l
		WHERE i.num = l.item_num
		GROUP BY num, url, serialized, processed
		""")
		
		conn.execute("""
			CREATE INDEX "items_processed" ON "raw_items" ("processed" ASC)
		""")
		
		conn.close()

	def __get_stored_items(self, property_as_str = None):
		"""
		Da todos los objetos Item almacenados con cierta propiedad expresada en
		SQL
		"""
		def yield_func(num, processed, serialized):
			return ItemManagerItem.get_stored_from_serialized(serialized)
		
		return self.__get_items_yield(property_as_str, yield_func)
	
	def __get_items(self, property_as_str = None):
		"""
		Da todos los ItemManagerItem que cumplan con una propiedad expresada
		en SQL
		"""
		def yield_func(num, processed, serialized):
			return ItemManagerItem(self, num, processed, serialized)
			
		
		return self.__get_items_yield(property_as_str, yield_func)
	
	def __get_items_yield(self, property_as_str, yield_func):
		"""
		Da todos los items que cumplan con una propiedad expresada en SQL,
		se convierte cada fila usando yield_func
		"""
		
		if property_as_str is None:
			property_as_str = "1"
		
		sql_count = """
		SELECT	COUNT(*) as count
		FROM	raw_items
		WHERE	%s
		""" % property_as_str
		
		sql_items = """
		SELECT	num, serialized, processed
		FROM	raw_items
		WHERE	%s
		""" % property_as_str
		
		conn_factory = _ConnFactory(self.__db_path)
		return DatabaseList(yield_func, conn_factory, sql_items, sql_count)
		

	
	def set_processed_from(self, min_item_num, processed):
		"""
		Pone todos los item desde el item <min_item_num> con el atributo
		processed con un valor dado
		"""
		check_if_any_type(min_item_num, int)
		if processed:
			processed = True
		else:
			processed = False
				
		with self.__lock:
			conn = self.__get_connection()
						
			conn.execute("""
			UPDATE	raw_items
			SET		processed = ?
			WHERE	num >= ?
			""",(processed, min_item_num))
			conn.commit()
			conn.close()
	
	@property
	def unprocessed_items(self):
		"Da los items sin procesar de la base de datos"
		with self.__lock:
			return self.__get_items("processed = 0")	
	
	@property
	def processed_items(self):
		"Da los items procesados de la base de datos"
		with self.__lock:
			return self.__get_items("processed = 1")
	
	@property
	def stored_unprocessed_items(self):
		"Da los items sin procesar de la base de datos como objetos Item"
		with self.__lock:
			return self.__get_stored_items("processed = 0")	
	
	@property
	def stored_processed_items(self):
		"Da los items procesados de la base de datos como objetos Item"
		with self.__lock:
			return self.__get_stored_items("processed = 1")
	
	@property
	def items(self):
		"Da todos los items de la base de datos"
		with self.__lock:
			return self.__get_items()
	
	def add(self, items):
		"Agrega un item (o una lista de ellos) como no procesado, como el item procesado más grande"
		with self.__lock:
			conn = self.__get_connection()
			
			if not hasattr(items, '__iter__'):
				items = [ items ]
			
			conn.executemany("""
			INSERT INTO raw_items (url, serialized, processed)
			VALUES (?, ?, ?)
			""", [ (item.url, pickle.dumps(item), False) for item in items ])
			conn.commit()
			conn.close()
	
	def add_error(self, item_num, error_message):
		with self.__lock:
			conn = self.__get_connection() 
			
			conn.execute("""
			INSERT INTO log (item_num, message)
			VALUES (?, ?)
			""", (item_num, error_message))
			conn.commit()
			conn.close()
		
	def set_processed(self, item_num, processed):
		"Pone el valor de processed en un item de la base de datos"
		with self.__lock:
			conn = self.__get_connection()
			
			conn.execute("""
			UPDATE	raw_items
			SET		processed = ?
			WHERE	num = ?
			""",
			(processed, item_num)) 
			conn.commit()
			conn.close()
	
	def set_stored_item(self, item_num, stored_item):
		"Pone el valor de serialized en un item de la base de datos"
		with self.__lock:
			conn = self.__get_connection()
			
			conn.execute("""
			UPDATE	raw_items
			SET		serialized = ?
			WHERE	num = ?
			""",
			(pickle.dumps(stored_item), item_num)) 
			conn.commit()
			conn.close()
		
	
class ItemManagerItem(object):
	"""
	Representa una copia del item guardado en el ItemManager
	"""
	
	def __init__(self, item_manager, item_num, processed, serialized):
		"""
		Crea una repres item a 
		"""
		self.__item_manager = item_manager
		
		self.__item_num = item_num
		self.__stored_item_serialized = serialized
		self.__processed = processed
		
		# Se usan para indicar que el item no fue deserealizado
		self.__stored_item_was_deserialized = False
		self.__stored_item_obj = None 
	
	@property
	def item_num(self):
		"Da el número de item"
		return self.__item_num
	
	@property
	def stored_item(self):
		"Da el item que se deserealizó de la base de datos"
		if not self.__stored_item_was_deserialized:
			self.__stored_item_obj = pickle.loads(self.__stored_item_serialized)
			self.__stored_item_was_deserialized = True
		return self.__stored_item_obj
	
	@classmethod
	def get_stored_from_serialized(cls, serialized):
		"Da el item desde el objeto serializado"
		return pickle.loads(serialized)
	
	def store_item(self):
		"""
		Guarda el contenido del item en el ItemManager de donde viene. 
		Los cambios hechos en stored_item no se reflejan si no se llama a este
		método
		"""
		self.__item_manager.set_stored_item(self.__item_num, self.stored_item)
	
	@property
	def processed(self):
		"Devuelve true si el item está procesado"		
		return self.__processed
	
	@processed.setter
	def processed(self, value):
		"Setea el valor de processed del item en la base de datos"
		check_if_any_type(value, bool)
		self.__item_manager.set_processed(self.__item_num, value)
		self.__processed = value
