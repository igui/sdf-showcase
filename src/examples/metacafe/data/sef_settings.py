'''
Created on 30/04/2010

@author: iavas
'''
import sdf.sef_settings
from examples.metacafe.data import Options

class SEFSettings(sdf.sef_settings.SEFSettings):
	"Las opciones para los parsers de metacafe"
	
	def __init__(self):
		sdf.sef_settings.SEFSettings.__init__(self)
		
	def get_options_class(self):
		"Retona la clase para Options. Por defecto es sdf.Options"
		return Options
