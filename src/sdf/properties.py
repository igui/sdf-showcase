# *- encoding: utf-8 -*
'''
Created on 17/03/2010

@author: ignacio
'''
import os.path
import re
import sys
from datetime import datetime

class Properties(object):
	'''
	Guarda propiedades de la aplicación (versión, etc)
	'''
	# la versión de svn
	__svn_ver = None

	@staticmethod
	def version():
		"Da la versión de SDF con información de svn"
		if Properties.__svn_ver == None:
			try:
				import sdf as __sdf
				s = os.path.sep
				entries_path = __sdf.__path__[0] + s + '.svn' + s + 'entries'
				entries_data = open(entries_path, 'r').read()
				svn_ver = re.search('dir\n(\d+)', entries_data).group(1)
			except IndexError as IOError:
				svn_ver = ""
			Properties.__svn_ver = svn_ver 

			
		if not Properties.__svn_ver:
			return Properties.__base_version()
		else:
			return "%s py%d.%d svn-%s" % (
								Properties.__base_version(),
								sys.version_info.major,
								sys.version_info.minor,
								Properties.__svn_ver
								)
		
	
	@staticmethod
	def __base_version():
		"Da la versión de SDF"
		return "1.5.0"

	@staticmethod
	def organization_domain():
		"Dominio de la organización"
		return "sdf.localdomain"

	@staticmethod
	def organization_name():
		"Nuestro nombre (SDF)"
		return "SDF"
	
	@staticmethod
	def copyright():
		"Nota de copyright"
		return str(datetime.now().year) + Properties.organization_name()
	
	@staticmethod
	def application_name():
		"Nombre de la aplicación"
		return "SDF"
	