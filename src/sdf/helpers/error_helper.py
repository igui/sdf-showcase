# *- encoding: utf-8 -*
import sys, traceback


class ErrorHelper(object):
	
	@staticmethod
	def get_last_error():
		"""
		Devuelve una cadena formateada conteniendo la última excepción ocurrida
		"""
		info = traceback.format_exception(*sys.exc_info())
		info = [i.strip() for i in info]
		str_error = info[-1].strip() + '\n' + \
					'\n'.join(info[1:-1]).strip().replace('\n\n', '\n')
		return 'Error: ' + str_error 