# *- encoding: utf-8 -*
'''
Created on 29/07/2010

@author: iavas
'''
from threading import Lock, currentThread
from sdf.util.typecheck import check_if_any_type
from sdf.page_parser import Page
from sdf.data.item import Item
from sdf.util.enum import Enum
from types import NoneType, FunctionType, MethodType
import sqlite3
import os
from pickle import dumps, loads
from copy import copy


def do_none(_):
	pass

class PageManagerBase(object):
	def add_item(self, page_handler, item):
		raise NotImplementedError
	
	def add_page(self, page_handler_parent_or_id, page):
		raise NotImplementedError
	
	def get_parser(self):
		raise NotImplementedError
	
	def set_page_state(self, val):
		raise NotImplementedError
	
	def add_error(self, val):
		raise NotImplementedError
	

class DefaultPageManager(PageManagerBase):
	'''
	Representa un manejador que administra las páginas pero de forma local
	'''

	def __init__(self, db_path, start_func, parser):
		PageManagerBase.__init__(self)
		
		check_if_any_type(db_path, str)
		check_if_any_type(start_func, (NoneType, FunctionType, MethodType))
		
		self.__parser = parser
		
		self.__db_path = db_path
			
		self.__connections_lock = Lock()
		#self.__connections = {}
		self.__connection = None	
		
		self.__add_page_listeners_lock = Lock()
		self.__add_page_listeners = []
		
		self.__lock = Lock()
		
		if start_func != None:
			# si se tiene que empezar con una base de datos nueva, borra el archivo
			if os.path.exists(db_path):
				os.remove(db_path)
			self.__init_db(start_func)
		else:
			if not os.path.exists(db_path):
				msg = "Continue last option specified, but '%s' was not found "
				msg += "to recover items"
				raise ValueError(msg % db_path)
			# chequea que exista la base de datos
			self.__prepare_db()
			

	def get_parser(self):
		return self.__parser

	def __get_connection(self):
		"Da la conexión respectiva a la base de datos"
		with self.__connections_lock:			
			if self.__connection == None or True:
				self.__connection = sqlite3.connect(self.__db_path)
				self.__connection.text_factory = str
				self.__connection.row_factory = sqlite3.Row
			
			return self.__connection
		
	def __prepare_db(self):
		conn = self.__get_connection()
		
		with conn:
			tables = conn.execute("""
				SELECT		name
				FROM		sqlite_master
			""").fetchall()
			tables = [ t[0] for t in tables ]
			
			# chequea que existan las tablas correspondientes
			expected_tables = ['pages', 'log', 'items']
			for t in expected_tables:
				if t not in tables:
					msg = "Database file '%s' doesn't seem to be a " 
					msg += "parser item database"
					raise LookupError(msg % self.__db_path)
		
			# borra las cosas pendientes, etc
			pendientes = conn.execute("""
				SELECT p.id
				FROM pages p, pages q
				WHERE p.parent = q.id and q.state = ? and p.state <> ?
			""", 
			(PageHandler.PageState.Finished, PageHandler.PageState.Finished))
			
			pendientes = [ (r[0],) for r in pendientes ]
			
			conn.executemany("""
				DELETE FROM items WHERE parent = ?
			""", pendientes)
			
			conn.executemany("""
				UPDATE pages SET state = 0 WHERE id = ? 
			""", pendientes)
			
			# borra a todos sus hijos y sus items 
			erased = pendientes
			while True:
				to_erase = conn.execute("""
				SELECT id
				FROM pages p
				WHERE parent IN (%s)
				""" % ','.join([ str(e[0]) for e in erased]) )
				
				to_erase = [ (r[0],) for r in to_erase ]
				
				if len(to_erase) == 0:
					break  
				
				conn.executemany("""
					DELETE FROM pages WHERE id = ?
				""", to_erase)
				
				conn.executemany("""
					DELETE FROM items WHERE parent = ?
				""", to_erase) 
				
				erased = to_erase
			conn.commit()
				
	
	def __init_db(self, start_func):
		conn = self.__get_connection()
		
		# Crea las tablas
		conn.execute("""
			CREATE TABLE "items" (
				"id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
				"parent" INTEGER NOT NULL ,
				"item_data" BLOB NOT NULL 
				)
		""")
		
		conn.execute("""
			CREATE TABLE "log" (
				"date" DATETIME NOT NULL  DEFAULT CURRENT_TIME,
				"page" INTEGER NOT NULL ,
				"message" TEXT NOT NULL
				)
		""")
		
		conn.execute("""
			CREATE TABLE "pages" (
				"id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
				"url" TEXT NOT NULL,
				"parent" INTEGER NOT NULL,
				"state" INTEGER NOT NULL,
				"priority" INTEGER NOT NULL,
				"page_data" BLOB NOT NULL
			)
		""")

		# crea los índices
		conn.execute('CREATE INDEX "pages__parent" ON "pages" ("parent" ASC)')
		conn.execute('CREATE INDEX "pages__state" ON "pages" ("state" ASC)')
		conn.execute("""
				CREATE UNIQUE INDEX "pages__id_parent" ON "pages"
				("id" ASC, "parent" ASC)
		""")
		conn.commit()
		
				
		# crea la página padre (la inicial)
		self.add_page(
						None,
						Page(
							url = '<start page>',
							parse = start_func,
							navigate = do_none
						)
				)
	
	def add_item(self, page_handler, item):
		"Agrega un item a la página"
		with self.__lock:
			conn = self.__get_connection()
			
			with conn:
				conn.execute("""
					INSERT INTO ITEMS (parent, item_data)
					VALUES (?,?)
				""", (page_handler.parent, dumps(item)))
				conn.commit()
		
	
	def add_page(self, page_handler_parent_or_id, page):
		"Agrega una página como hija de cierta página"
		with self.__lock:
			check_if_any_type(page, Page)
	
			if page_handler_parent_or_id == None:
				parent_id = -1
			elif isinstance(page_handler_parent_or_id, PageHandler):
				parent_id = page_handler_parent_or_id.id
			elif isinstance(page_handler_parent_or_id, int):
				parent_id = page_handler_parent_or_id
			else:
				raise ValueError("page_handler_parent_or_id has invalid type") 
	
			conn = self.__get_connection()
			cursor = conn.cursor() 
			
			serialized = copy(page)
			serialized._set_parser_instance(None)
			serialized = dumps(serialized)
			
			cursor.execute("""
				INSERT INTO pages	(url, parent, state, priority, page_data)
				VALUES				(?, ?, ?, ?, ?)
			""", 
				(page.url, parent_id, PageHandler.PageState.Pending,
				 page.priority, serialized)
			)
			conn.commit()

		# avisa a los escuchas
		page_handler = PageHandler(cursor.lastrowid, page, parent_id, self)
		with self.__add_page_listeners_lock:
			for l in self.__add_page_listeners:
				l.on_add_page(self, page_handler)
				
			
	def on_add_page_suscribe(self, on_add_page_listener):
		"Se suscribe al evento on_add_page"
		check_if_any_type(on_add_page_listener, AddPageListener)
		
		with self.__add_page_listeners_lock:
			self.__add_page_listeners.append(on_add_page_listener)
			
	
	def get_pending_page(self):
		"Devuelve una página pendiente de procesamiento y lo pone como procesado"
		with self.__lock:
			conn = self.__get_connection() 
			
			with conn:
				cursor = conn.execute("""
					SELECT id, parent, page_data
					FROM pages
					WHERE state = ? 
					ORDER BY priority ASC
					LIMIT 0,1
					
				"""	, (PageHandler.PageState.Pending,)) 
				
				row = cursor.fetchone()
				
				if row == None:
					return None
				
				# levanta el page_handler
				page = loads(row['page_data'])
				page_handler = PageHandler(row['id'], page, row['parent'], self)
				page_handler._set_state(PageHandler.PageState.Processing)
				
				cursor.execute("""
					UPDATE pages
					SET state = ?
					WHERE id = ?
				""", (PageHandler.PageState.Processing, page_handler.id))
				conn.commit()
			
				return page_handler
			
		
	def set_page_state(self, page_handler, state):
		"Pone una página como finalizada"
		with self.__lock:
			conn = self.__get_connection()
			with conn:
				conn.execute("""
					UPDATE pages
					SET state = ?
					WHERE id = ?
				""", (state, page_handler.id))
				
				page_handler._set_state(state)
			conn.commit()
			
	def add_error(self, page_id, error_str):
		"Agrega un error a la lista de errores"
		with self.__lock:
			conn = self.__get_connection()
			with conn:
				conn.execute("""
					INSERT INTO log (page, message) VALUES (?, ?)
				""", (page_id, error_str))
				conn.commit()
	
	def get_processed_items(self):
		with self.__lock:
			conn = self.__get_connection()
			cursor = conn.cursor()
			
			cursor.execute("""SELECT item_data FROM items""")
			res = []
			while True:
				r = cursor.fetchone()
				if r == None:
					break
				res.append(loads(r[0]))
				
			return res 
		
	def get_unprocessed_items(self):
		return []
	
	def count_pages(self):
		"""
		Cuenta las páginas y devuelve las procesadas y la cantidad total
		en un par del tipo ``(finalizadas, total)``
		"""
		with self.__lock:
			conn = self.__get_connection()
			
			with conn:
				rows = 	conn.execute("""
					SELECT state, COUNT(*)
					FROM pages
					GROUP by state
				""")
				
				conn.commit()
				
				res = { }
				for r in rows:
					res[r[0]] = r[1]
					
				finished = res.get(PageHandler.PageState.Finished, 0) 
				failed = res.get(PageHandler.PageState.Failed, 0)
				total = sum(res.values())
				
				return (finished + failed, total)

class ItemHandler(object):
	"Un elemento que maneja un objeto Item"
	
	def __init__(self, id, item, parent):
		check_if_any_type(id, (int, int))
		self.__id = id
		check_if_any_type(parent, (PageHandler))
		self.__parent = parent
		check_if_any_type(item, Item)
		self.__item = item	
	
	@property
	def id(self):
		return self.__id
	
	@property
	def parent(self):
		return self.__parent
	
	@property
	def item(self):
		return self.__item
		
class PageHandler(object):
	"Un elemento que maneja un objeto Page de PageParser"
	PageState = Enum(Pending = 0, Processing = 1, Finished = 2, Failed = 3)
	
	def __init__(self, id, page, parent, page_manager):
		check_if_any_type(id, (int, int))
		self.__id = id
		
		check_if_any_type(parent, (NoneType, PageHandler, int, int))
		if parent == None:
			self.__parent =	-1
		elif isinstance(parent, PageHandler):
			self.__parent = parent.id
		else:
			self.__parent = parent
			
		check_if_any_type(page_manager, DefaultPageManager)
		self.__page_manager = page_manager
		
		check_if_any_type(page, Page)
		self.__page = page
		self.__page._set_parser_instance(page_manager.get_parser())
				
		self.__page_state = self.PageState.Pending
		
	
	def add_item(self, item):
		self.__page_manager.add_item(self, item)
		
	def add_page(self, page):
		self.__page_manager.add_page(self, page)
	
	@property
	def id(self):
		return self.__id
	
	@property
	def page(self):
		return self.__page
		
	@property
	def parent(self):
		return self.__parent
	
	@property
	def state(self):
		return self.__page_state
	
	@state.setter
	def state(self, val):
		self.__page_manager.set_page_state(self, val)
	
	def _set_state(self, val):
		"Deberóa llamarse solo desde page_manager"
		self.__page_state = val
	
	def store(self):
		"Guarda el valor de la página"
		pass
	
class AddPageListener(object):
	"Un escucha para la función on add_page de page_manager"
	
	def on_add_page(self, page_manager, page_handler):
		"Se llama al hacer on_add_page"
		raise NotImplementedError
		