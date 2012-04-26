# *- encoding: utf-8 -* 
'''
Created on 30/03/2010

@author: iavas
'''
from datetime import datetime
from sdf.util.typecheck import check_if_any_type, check_if_integral
from .util import Enum
import sys
from sdf.file_logger import FileLogger
from sdf.redirect_writer import RedirectWriter
import sqlite3
import tempfile
from threading import Lock


class Logger(object):
	'''
	Una clase que loguea mensajes y avisa de estos eventos a otros observadores
	'''
	MessageLevel = Enum(Info=10, Debug=20, Error=0)
	"El nivel de los mensajes del log"

	def __init__(self):
		self.__observers = [ ]
		self.__lock = Lock()
		
	def log(self, message, level= None):
		"Manda un mensaje al log"
		if level == None:
			level = self.MessageLevel.Info
		
		with self.__lock:
			now = datetime.now()
			for observer in self.__observers:
				try:
					observer.on_log(now, message, level)
				except UnicodeEncodeError as ex:
					observer.on_log(
								now,
								message.encode('ascii', 'backslashreplace'),
								level
								)
			
		
				
	def subscribe(self, logger_observer):
		"Añade una observador para manejar cuando se loguea un evento en el log"
		check_if_any_type(logger_observer, LoggerObserver)
		with self.__lock:
			self.__observers.append(logger_observer)
			
	def unsuscribe_all(self):
		"Saca a todos los observadores del logger"
		with self.__lock:
			self.__observers = []


class LoggerObserver(object):
	"Modela un observador para un log de mensajes"
	def on_log(self, date, message, level):
		"Se llama cuando se llama a la función log() del logger"
		raise NotImplementedError


class RedirectLogger(Logger, LoggerObserver):
	"Un logger que redirecciona a otro logger más"
	def __init__(self, main_logger):
		Logger.__init__(self)
		check_if_any_type(main_logger, MainLogger)
		self.__main_logger = main_logger
		self.subscribe(self)
		
	def on_log(self, date, message, level):
		self.__main_logger.log_from_stream(date, message, level)
		

class MainLogger(Logger, LoggerObserver):
	"""
	Un logger que redirecciona la salida estándar y el error estándar a sí mismo
	"""
	
	def __init__(self):
		Logger.__init__(self)
		self.__messages = _MessageManager()
		self.__init_date = datetime.now()
		self.__end_date = None
		self.__original_stdout = sys.stdout
		self.__redirect_streams()
		
		self.unsuscribe_all()
		self.subscribe(self)
		

	def __redirect_streams(self):
		"Redirecciona los flujos estándar al logger"
		encoding = sys.stdout.encoding
		if encoding == None:
			encoding = 'utf-8'
		
		stdout_redirects = [
						sys.stdout,
						FileLogger(RedirectLogger(self), encoding)
						]
		sys.stdout = RedirectWriter(stdout_redirects, encoding)
		
		
		stderr_redirects = [
						sys.stderr,
						FileLogger(RedirectLogger(self), encoding)
						]
		sys.stderr = RedirectWriter(stderr_redirects, encoding)
		
	
	def on_log(self, date, message, level):
		"Se llama cuando se llama a la función log() del logger"
		encoding = sys.stdout.encoding
		if encoding == None:
			encoding = 'utf-8'
		
		for line in message.splitlines():
			print((("[%s] " % date.strftime("%H:%M:%S")) + line), file=self.__original_stdout)
			
		self.__messages.add_message(date, message, level)
	
	def log_from_stream(self, date, message, level):
		"Usada para los logs externos"
		self.__messages.add_message(date, message, level)
			
	def iter_messages(self):
		"""
		Devuelve los mensajes logueados
		"""
		return self.__messages.iter_messages()
	
	def get_last_messages(self, n):
		"Da los últimos n mensajes."
		return self.__messages.get_last_messages(n)
	
	def mark_end(self):
		"Marca el fin del logging"
		self.__end_date = datetime.now()
		
	@property
	def init_date(self):
		"La fecha en la que se inció el parseo"
		return self.__init_date
	
	@property
	def end_date(self):
		"La fecha en la que finalizó el parseo o None si aún sigue corriendo"
		return self.__end_date
		
	
class DefaultLoggerObserver(LoggerObserver):
	"Un observador del log"
	def __init__(self):
		LoggerObserver.__init__(self)
		
	def on_log(self, date, message, level):
		encoding = sys.stdout.encoding
		if encoding == None:
			encoding = 'utf-8'
		
		for line in message.splitlines():
			line = line.decode(encoding, 'replace')
			print(("[%s] " % date.strftime("%H:%M:%S")) + line)


class LoggerMessage(object):
	"Un mensaje generado por el log"
	def __init__(self, date, msg, level):
		check_if_any_type(date, datetime)
		check_if_any_type(msg, str)
		check_if_integral(level)
				
		self.__date = date
		self.__msg = msg
		self.__level = level
		
	@property
	def date(self):
		"La fecha del mensaje"
		return self.__date
	
	@property
	def msg(self):
		"El string del mensaje"
		return self.__msg
	
	@property
	def level(self):
		"El nivel del mensaje"
		return self.__level


class _MessageManager(object):
	"Maneja los mensajes generados por el log en una base de datos temporal"
	
	def __init__(self):
		self.__db_path = tempfile.mktemp(".db", "sdf-log-",)
	
		conn = self.__get_connection()
		conn.executescript("""
			CREATE TABLE "messages" (
			    "id" INTEGER PRIMARY KEY NOT NULL,
			    "message" TEXT NOT NULL,
			    "date" DATETIME NOT NULL,
			    "level" INTEGER NOT NULL
			);
		""")
		conn.commit()
		conn.close()
		
	def __get_connection(self):
		"Da la conexión respectiva a la base de datos"
		self.__connection = sqlite3.connect(
				self.__db_path,
				detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
				)
		self.__connection.text_factory = str
		self.__connection.row_factory = sqlite3.Row
			
		return self.__connection 
	
	def add_message(self, date, msg, level):
		"Agrega un mensaje a la lista de mensajes logueados"
		check_if_any_type(date, datetime)
		check_if_any_type(msg, str)
		check_if_integral(level)
						
		conn = self.__get_connection()
		with conn:
			conn.execute("""
				INSERT INTO messages (message, date, level)
				VALUES (?, ?, ?)
			""", (msg, date, level)
			)
			conn.commit()

	def iter_messages(self):
		"Da un iterador en los mensajes logueados"
		
		conn = self.__get_connection()
		with conn:
			messages = conn.execute("""
				SELECT		message, date as "d [timestamp]", level
				FROM		messages
				ORDER BY	id
			"""
			)
			
			for r in messages:
				yield LoggerMessage(r[1], r[0], r[2])
			messages.close()
			
	def get_last_messages(self, n):
		"Da los últimos n mensajes"
		check_if_integral(n)
		if n < 0:
			raise ValueError("n es negativo")
		
		conn = self.__get_connection()
		with conn:
			messages = conn.execute("""
				SELECT		message, date as "d [timestamp]", level
				FROM		messages
				ORDER BY	id DESC
				LIMIT		?
			""", (n,)
			)
			res = []
			for r in messages:
				res.append(LoggerMessage(r[1], r[0], r[2]))
			messages.close()
			
			return [ r for r in reversed(res) ] 
