# *- encoding: utf-8 -*
'''
Created on 08/12/2010

@author: iavas
'''
from .postaction import PostAction
from sdf.util.ftp_handler import FTPHandler

class FTPUploader(PostAction):
	'''
	Una postaction que sube el resultado de la corrida a un servidor FTP.
	El parámetro host es el nombre o IP del servidor FTP. Los parámetros user
	y passwd son el usuario y clave para usar en dicho servidor.	
	'''
	
	def __init__(self, host, user, passwd):
		PostAction.__init__(self)
				
		self.__host = host
		self.__user = user
		self.__pass = passwd
		self.__ftp_handler = FTPHandler()
	
	def run(self, context, result):
		
		if result == 0:
			# Proceso finalizó correctamente: subo la salida.
			try:
				self.__ftp_handler.upload_file(
					host_url=self.__host,
					user_id=self.__user,
					user_pass=self.__pass,
					file_name=context.options.output_file
				)
				print('Archivo enviado al servidor FTP correctamente')
			except Exception as ex:
				print('Error en FTPUploader: ' + str(ex))
		else:
			print('El parser no finalizo correctamente. Omitiendo FTP...')
		
		