# *- encoding: utf-8 -*
'''
Created on 10/12/2010

@author: iavas
'''
from sdf.util.typecheck import check_if_any_type
from .postaction import PostAction

class PostActionManager(object):
	'''
	Maneja las postactions de un parser
	'''

	def __init__(self, context):
		from sdf import Context
		check_if_any_type(context, Context)
		self.__context = context
		self.__postactions = []
	
	
	def add_postaction(self, postaction):
		"Agrega una postaction para correr"
		check_if_any_type(postaction, PostAction)
		self.__postactions.append(postaction)
	
	@property
	def postactions(self):	
		"Devuelve las postactions a correr"
		return self.__postactions
	
	