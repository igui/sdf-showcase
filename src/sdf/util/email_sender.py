#! *- encoding: utf-8 -*
'''
Created on 26/07/2010

@author: AlejandroM
'''

import smtplib
from email.utils import COMMASPACE
from email.mime.multipart import MIMEMultipart
from mimetypes import guess_type
from email.mime.base import MIMEBase

class EmailError(Exception):
	'''
	Clase de excepcion para la clase EmailSender.
	'''
	
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)


class EmailSender(object):
	'''
	Clase que envía correos electrónicos utilizando la cuenta de SDF.
	
	Ejemplo breve de uso: ::
					
		mailer = EmailSender()	
		msg = ' Hola!\nChau!'	
		mailer.send_mail(to_addr=['spam@mail.com', 'eggs@mail.com'], msg=msg, subject='Prueba mail')	
		mailer.close()	
	'''

	def __init__(self, server='smtp.gmail.com', user='general@gmail.com', passwd='*xp06flush'):
		'''
		Constructor
		'''
		# Establecemos conexion con el servidor smtp de gmail
		self._server = server		
		self._user = user		
		try:
			self._mail_server = smtplib.SMTP(server, 587)					
			self._mail_server.ehlo()
			self._mail_server.starttls()
			self._mail_server.ehlo()			
			self._mail_server.login(user, passwd)
		except smtplib.SMTPAuthenticationError as e:
			raise EmailError('Usuario o clave incorrectos: %s' % (str(e)))
		except Exception as e:
			raise EmailError('Imposible conectar al servidor de correo %s: %s' % (server, str(e)))
	
	def send_mail(self, to_addr, msg, from_addr='SDF Report', subject='Aviso SDF',
				   from_header='SDF Report', rply_to_header='no-reply',
				   attach_files = []):
		
		to_header= to_addr
		if hasattr(to_header, '__iter__'):
			to_header = COMMASPACE.join(to_header)
			
		mime_msg = MIMEMultipart()				 
		mime_msg['From'] = from_header
		mime_msg['Reply-to'] = rply_to_header
		mime_msg['To'] = to_header		
		mime_msg['Subject'] = subject
		
		mime_msg.attach(MIMEText(msg, 'html'))
		
		for filepath, filename in attach_files:
			mimetype_root, mimetype_sub = guess_type(filename)
			if mimetype_root == None:
				mimetype_root, mimetype_sub = 'application', "octet-stream"
			
			part = MIMEBase(mimetype_root, mimetype_sub)
			part.set_payload(open(filepath,"rb").read())
			Encoders.encode_base64(part)
			part.add_header(
					'Content-Disposition',
					'attachment; filename="%s"' % filename
					)
			mime_msg.attach(part)


		self._mail_server.sendmail(from_addr, to_addr, mime_msg.as_string())		


	def close(self):
		self._mail_server.close()
