# *- encoding: utf-8 -*

class DataAdapter(object):
	"""
	Clase base de data_adapter. Todos los métodos son opcionales, si no se
	sobreescribe ninguno el adapter no hace nada al llamar a los métodos, es
	dummy
	"""
	def __init__(self):
		pass

	def write_state(self):
		"""
		Escribe el estado del parser para que se pueda reanudar en una
		próxima ejecución
		""" 
		pass
	
	def write_log(self, log_type, message, url=None):
		"Escribe un mensaje en el log"
		print("Log: type=%s url=%s message=%s" % (log_type, message, url))
	
	def write_item(self, item, unique=True):
		"Persiste un item en la base de datos"
		pass
	
	def write_items(self, items):
		"Persiste una serie de items a la base de datos"
		for item in items:
			self.write_item(item)
	
	def clean(self):
		"""
		Limpia el estado del parser, borrando los items que pueda contener y
		toda la información que este tenga
		"""
		pass
	
	def commit_items(self):
		"""
		Se llama cuando hay que confirmar los items en el almacenamiento
		persistente, util si el data_adapter adapta a una base de datos relacional
		"""
		pass
	
	def commit(self, write_state = True, commit_items = True):
		"""
		Confirma los items sin confirmar (si aplica al data_adapter) y escribe
		el estado
		"""
		if write_state:
			self.write_state()
		if commit_items:
			self.commit_items()
	
	def close(self):
		"""
		Se llama cuando el data_adapter no se va a usar más
		"""
		pass
		
		