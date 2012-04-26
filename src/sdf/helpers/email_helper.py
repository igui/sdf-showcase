# *- encoding: utf-8 -*
import re
from sdf.util import deprecated

class EmailHelper(object):
	
	def __init__(self, context):
		self.context = context
		self.__res_email = {}
		self.__res_email['@'] = re.compile('((?:[a-zA-Z0-9_\-\.]+))@((?:(?:\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(?:(?:[a-zA-Z0-9\-]+\.)+))(?:[a-zA-Z]{2,4}|[0-9]{1,3}))')
		self.__res_email[' (at) '] = re.compile('((?:[a-zA-Z0-9_\-\.]+))\s\(at\)\s((?:(?:\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(?:(?:[a-zA-Z0-9\-]+\.)+))(?:[a-zA-Z]{2,4}|[0-9]{1,3}))')
		self.__res_email['(at)'] = re.compile('((?:[a-zA-Z0-9_\-\.]+))\(at\)((?:(?:\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(?:(?:[a-zA-Z0-9\-]+\.)+))(?:[a-zA-Z]{2,4}|[0-9]{1,3}))')
		
	@deprecated
	def fill(self, type, text, item, exclude=[], at_sign = '@'):
		text = self.context.text_helper.get_text(text)
		re_email = self.__res_email[at_sign]
		for m_email in re_email.finditer(text):
			email = re_email.sub('\g<1>@\g<2>', m_email.group(0).strip().lower())
			if email not in exclude and  email not in item.email_empresa:
				item.email_empresa.append(email)

	def extract(self, text, at_sign = '@', exclude=[]):
		"""
		Extrae los mails delimitados por @, devuelve una lista con los mails
		  
		Parámetros
		
		*text*
		
			El texto donde buscar
			
		*at_sign*
		
			La forma del símbolo separador (arroba) Los valores soportados son
			``"@"`` , ``"  (at)  "`` o '(at)'
			
		*exclude*
		
			Lista de emails a excluir 
		
		Devuelve
			Una lista con los mails
		"""
		res = []
		re_email = self.__res_email[at_sign]
		for m_email in re_email.finditer(text):
			email = re_email.sub('\g<1>@\g<2>', m_email.group(0).strip().lower())
			if email not in exclude and email not in res:
				res.append(email)
		return res
	
	@staticmethod
	def extract_email(text):
		"""
		Extrae el mail de un texto cualquiera y devuelve el mail extraído o
		tira ValueError si text no coincide con una cadena de mail
		"""
		match = re.search('((?:[a-zA-Z0-9_\-\.]+))@((?:(?:\[[0-9]{1,3}\.[0-9]{1,3}' + 
						'\.[0-9]{1,3}\.)|(?:(?:[a-zA-Z0-9\-]+\.)+))' +
						'(?:[a-zA-Z]{2,4}|[0-9]{1,3}))', text)
		if not match:
			raise ValueError("'%s' didn't match regular expression" % text)		
		return match.group()
	