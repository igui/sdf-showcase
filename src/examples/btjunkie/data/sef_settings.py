# *- encoding: utf-8 -*
'''
Created on 30/04/2010

@author: iavas
'''
import sdf.sef_settings
from examples.btjunkie.data import Options
from sdf.postactions import MailSender

class SEFSettings(sdf.sef_settings.SEFSettings):
	"Las opciones para los parsers de btjunkie"
	
	def __init__(self):
		sdf.sef_settings.SEFSettings.__init__(self)
		
	def get_options_class(self):
		"Retona la clase para Options. Por defecto es sdf.Options"
		return Options

	def get_postactions(self):
		"""
		Retorna las postactions a ejecutar en el órden de ejecución. Por
		defecto retorna la lista vacía
		"""
		return [ ]
	