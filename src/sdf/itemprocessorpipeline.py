# *- encoding: utf-8 -*
'''
Created on 27/01/2010

@author: iavas
'''

from threading import Lock, Condition, Thread
from sdf.util import synchronized_method
from collections import deque
import traceback
import sys
import collections

class ItemProcesorPipeline(object):
	"""
	Ayuda a procesar un conjunto de items(una función con parámetros) en paralelo
	"""
	
	# la prioridad que tienen los items cuando no se especifica su prioridad
	__DEFAULT_PRIORITY = 0
	
	def __init__(self, nthreads):
		"""
		Inicializa el pipeline. Puede procesar hasta <nthreads> en paralelo  
		"""
		
		if nthreads < 1:
			raise ValueError("nthreads must be at least 1")
		
		# Variables de sincronización
		self.lock = Lock()
		self.__events_queue = deque()
		self.__events_queue_non_empty = Condition()
		self.__items_queue = deque()
		self.__finished = Condition()

		
		# los hilos que están corriendo un item están en False, los otros están
		# en True
		self.__worker_threads = {
			# libres
			True: set([ 
				_PipelineWorkerThread(i+1, self) for i in range(nthreads)
			]),
			
			# corriendo un item
			False : set([]) 
		}
		
		# Inicia el hilo de control de pipeline
		worker = Thread(target = ItemProcesorPipeline.__controller_thread_func,
					args = (self, ) )
		worker.name = "ItemProcesorPipeline-Main"
		worker.daemon = True
		worker.start() 
	
	@synchronized_method('lock')
	def push(self, func, *args, **kw):
		"""
		Agrega un item al pipeline para ser procesado
		"""
		# print "!push"
		if not isinstance(func, collections.Callable):
			raise TypeError("func is not callable")
		
		self.__events_queue_non_empty.acquire()
		priority = self.__DEFAULT_PRIORITY
		self.__events_queue.append(_PipelineItem(func, args, kw, priority))
		self.__events_queue_non_empty.notifyAll()
		# print "!push notified"
		self.__events_queue_non_empty.release()
	
	
	@synchronized_method('lock')
	def cancel_queue(self):
		"""
		Cancela todas las ejecuciones pendientes en la cola de eventos. Las
		que estaban corriendo en el instante de la llamada siguen así.
		self.wait_end() no termina hasta que esas llamadas finalizen
		"""
		self.__events_queue_non_empty.acquire()
		# lo agrega al principio de la cola
		self.__events_queue.appendleft(_CancelQueueItem())
		self.__events_queue_non_empty.notifyAll()
		self.__events_queue_non_empty.release()
	
	
	@synchronized_method('lock')
	def wait_end(self):
		"Espera hasta que se hayan procesado todos los items"

		if not self.__has_finished():
			self.__finished.acquire()
			## print "!wait start"
			self.lock.release()
			self.__finished.wait()
			self.lock.acquire()
			self.__finished.release()
		
	
	@synchronized_method('lock')	
	def _on_pipeline_worker_end(self, worker, ex, traceback):
		self.__events_queue_non_empty.acquire()
		self.__events_queue.append(_PipelineWorkerThreadResult(worker, ex, traceback))
		self.__events_queue_non_empty.notifyAll()
		self.__events_queue_non_empty.release()
		
		
	def __has_finished(self):
		"Devuelve true sii el pipeline no tiene items corriendo o pendientes"
		return	len(self.__items_queue) == 0 and \
				len(self.__worker_threads[False]) == 0 and \
				len(self.__events_queue) == 0
	
	def __process_event(self, event):
		"Procesa un evento recibido en la cola de eventos"
		## print "!process event"
		
		# item para correr
		if isinstance(event, _PipelineItem):
			# hay algún worker libre
			if len(self.__worker_threads[True]) > 0:
				worker_thread = self.__worker_threads[True].pop()
				self.__worker_threads[False].add(worker_thread)
				worker_thread.exec_func(event.func, event.args, event.kw)
			else:
				self.__items_queue.append(event)
				
		# un worker terminó de correr la función 
		elif isinstance(event, _PipelineWorkerThreadResult):
			if event.exception_obj != None:
				print(event.traceback, file=sys.stderr) 
			
			# pone al thread como libre
			self.__worker_threads[False].remove(event.worker)
			self.__worker_threads[True].add(event.worker) 
			
			if self.__has_finished(): 
				self.__finished.acquire()
				self.__finished.notifyAll()
				self.__finished.release()
				
			elif len(self.__items_queue) > 0:
				item = self.__items_queue.popleft()
				worker_thread = self.__worker_threads[True].pop()
				self.__worker_threads[False].add(worker_thread)
				worker_thread.exec_func(item.func, item.args, item.kw)
		
		elif isinstance(event, _CancelQueueItem):
			# limpia toda la cola de items pendientes
			self.__items_queue.clear()
		
		else:
			raise TypeError("Object Type wasn't expected: %s ", type(event))
				
			
		
	def __controller_thread_func(self):
		"Función principal de control de hilos del pipeline"

		self.lock.acquire()
		while True:
			# print "!loop pipeline"
			if len(self.__events_queue) == 0:
				self.__events_queue_non_empty.acquire()
				self.lock.release()
				# print "!event wait started"
				self.__events_queue_non_empty.wait()
				self.__events_queue_non_empty.release()
				# print "!event received"
				self.lock.acquire()
			
			while len(self.__events_queue) > 0:
				event = self.__events_queue.popleft()
				self.__process_event(event)
		
class _PipelineWorkerThread(Thread):
	"""Un hilo que ejecuta una función y avisa al terminar
		al processor pipeline
	"""
	
	def __init__(self, number, processor_pipeline):
		"""
		Inicializa el hilo
		Parámetros
		number -- número de hilo
		processor_pipeline -- la variable a la aque avisa al terminar de correr 
		"""
		
		self.__processor_pipeline = processor_pipeline
		
		Thread.__init__(self)
		self.name = "ItemProcesorPipeline-Worker-%d" % number
		self.daemon = True
		
		self.lock = Lock()
		self.__wait_for_fun = Condition()
		self.__fun = None
		self.__fun_args = None
		self.__fun_kw = None
		
		self.start()
		
	def run(self):
		self.lock.acquire()
		while True:
			self.__wait_for_fun.acquire()
			# print "self.__wait_for_fun.acquire()"
			self.lock.release()
			self.__wait_for_fun.wait()
			# print "self.__wait_for_fun.wait()"
			self.lock.acquire()
			try:
				self.__fun(*self.__fun_args, **self.__fun_kw)
			except Exception as ex:
				self.__wait_for_fun.release()
				self.__processor_pipeline._on_pipeline_worker_end(self, ex,
					traceback.format_exc())
			else:
				self.__wait_for_fun.release()
				self.__processor_pipeline._on_pipeline_worker_end(self, None,
					None)
	
	@synchronized_method('lock')		
	def exec_func(self, func, args, kw):
		"""
		Pone una función a correr, esta avisa al terminar llamando a 
		_on_pipeline_worker_end
		"""
		self.__wait_for_fun.acquire()
		
		self.__fun = func
		self.__fun_args = args
		self.__fun_kw = kw

		self.__wait_for_fun.notifyAll()
		self.__wait_for_fun.release()

class _PipelineWorkerThreadResult(object):
	"Modela el resultado de una ejecución de un item en el pipeline"
	
	def __init__(self, worker, ex, traceback):
		"""
		Constructor, toma la excepción causada por la función o None si no hubo
		"""
		self.__exception_obj = ex
		self.__traceback = traceback
		self.__worker = worker
		
	@property
	def worker(self):
		return self.__worker	
	
	@property
	def exception_obj(self):
		return self.__exception_obj 
	
	@property
	def traceback(self):
		return self.__traceback			
		
class _PipelineItem(object):
	"Representa un item a procesar en paralelo junto a otros"
	
	def __init__(self, func, args, kw, priority):
		self.__func = func
		self.__args = args
		self.__kw = kw
		self.__priority = priority

	@property
	def func(self):
		return self.__func
	
	@property
	def args(self):
		return self.__args
	
	@property
	def kw(self):
		return self.__kw
	
	def __cmp__(self, der):
		"Se implementa para poder usarlos en colas de prioridad"
		if isinstance(der, _PipelineItem):
			# se comparan por prioridad
			return self.__priority - der.__priority
		elif isinstance(der, _CancelQueueItem): 
			# los _CancelQueueItem tienen siempre más prioridad 
			# (self > der siempre)
			return 1
		else:
			raise TypeError("invalid argument for compare")
		

class _CancelQueueItem(object):
	"Una clase dummy para indicar que termina el procesamiento"
	
	def __cmp__(self, der):
		"Se implementa para poder usarlos en colas de prioridad"
		if isinstance(der, _CancelQueueItem):
			return 0
		elif isinstance(der, _PipelineItem): 
			# los _CancelQueueItem tienen siempre más prioridad 
			# (self < der siempre)
			return -1
		else:
			raise TypeError("invalid argument for compare")