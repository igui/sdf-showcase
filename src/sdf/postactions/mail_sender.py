# *- encoding: utf-8 -*
'''
Created on 08/12/2010

@author: iavas
'''
from .postaction import PostAction
from sdf.util.email_sender import EmailSender
from string import Template
from datetime import datetime
from io import StringIO
from cgi import escape
from sdf import Logger
from tempfile import mktemp
from os import remove
from os import path
import sys
from sdf.util.typecheck import check_if_any_type
from types import NoneType

class MailSender(PostAction):
	'''
	Una postaction que envía un mail con información acerca del resultado
	de la corrida. El parámetro to tiene la lista de destinatarios del mail de 
	reporte y proyect es el nombre del proyecto para poner en los títulos del 
	mail
	'''
	
	def __init__(self, to, project = None):
		PostAction.__init__(self)
		
		if not hasattr(to, '__iter__'):
			to = [ to ]
		for t in to:
			if not isinstance(t, str):
				raise ValueError("to debe ser una lista de strings o un string")
			
		check_if_any_type(project, [NoneType, str])
		
		self.__project = project
		self.__to = to

	
	def __get_messages_html(self, context, n):
		"Da el html de los últimos n mensajes"
		messages = StringIO()
		for m in context.logger.get_last_messages(n):
			message_template = Template(self.__mail_message_template)
			
			date_str = m.date.strftime("%H:%M:%S")
			if m.level == Logger.MessageLevel.Error:
				message_color = "red"
			else:
				message_color = "black"
			
			
			message_part = message_template.substitute(
							date = escape(date_str),
							message = escape(m.msg),
							message_color = message_color
							)
				
			print(message_part, file=messages)
			
		return messages.getvalue()
	
	
	def __make_temp_log_file(self, context):
		"Arma un archivo con los logs y devuelve la ruta"
		filename = mktemp(".txt", "sdf-log-report")
		
		f = open(filename, "w")
		for m in context.logger.iter_messages():
			print(m.msg, file=f)
		f.close()
			
		return filename 	
	
	def __get_parser_name(self, context):
		"Da el nombre del parser (el módulo que lo contiene)"
		return context.parser_name		
	
	def __make_dict(self, context, result):
		"Arma un diccionario con variables usadas para el mail"
		start = context.logger.init_date.strftime("%d/%m/%y %H:%M:%S")
		end = context.logger.end_date
		if end == None:
			end = datetime.now()
		end = end.strftime("%d/%m/%y %H:%M:%S")
			
		if result == 0:
			res = "correctamente"
			res_subject = "OK"
			title_color = "#7ACAFF"
		else:
			res = "con errores"
			res_subject = "ERROR"
			title_color = "#BB0000"
			
		parser_name = self.__get_parser_name(context)

		# arma mensaje
		cant_mensajes = 50		
		messages = self.__get_messages_html(context, cant_mensajes)

		if self.__project == None:
			project = ""
			subject_project = ""
		else:
			project = "(%s)" % self.__project
			subject_project = self.__project

		res = dict(
			parser			= parser_name,
			res				= res,
			title_color		= title_color,
			start			= start,
			end				= end,
 			messages		= messages,
 			res_subject		= res_subject,
 			parser_name		= parser_name,
 			project			= project,
 			subject_project = subject_project
		)
		
		return res

	def customize_message_vars(self, context, result, message_vars):
		"""
		Usado por clases derivadas para personalizar las variables del mensaje.
		Context y result son las mismas que en :func:`run()` y message_vars 
		es un diccionario con las siguientes claves
		
		=============== ==================================================
		Clave           Descripción
		=============== ==================================================
		parser          el nombre del parser
		res             el resultado como aparece en el mensaje
		title_color     el color de la barra al prinicipio del mensaje
		start           la hora de inicio
		end             la hora de fin
		messages        la cadena de mensajes
		res_subject     el resultado en el asunto del mensaje
		parser_name     el nombre del parser
		project         el nombre del proyecto en el cuerpo del mensaje
		subject_project el nombre del proyecto en el asunto del mensaje
		=============== ==================================================
		
		Al finalizar el método message_vars debe tener las variables que
		modificó el usuario.
		"""
		pass
	
	def run(self, context, result):
		mailer = EmailSender()    

		message_vars = self.__make_dict(context, result)
		self.customize_message_vars(context, result, message_vars)
				
		msg = Template(self.__mail_template_html).substitute(message_vars)
		
		# arma asunto
		if self.__project == None:
			vars = (
				message_vars['end'],
				message_vars['res_subject'],
				message_vars['parser_name']
				)
			subject = '[Reporte SDF][%s][%s] %s' % vars 
		else:
			vars = (
				message_vars['subject_project'],
				message_vars['end'],
				message_vars['res_subject'],
				message_vars['parser_name']
				)
			subject = '[%s][%s][%s] %s' % vars
		
		# arma archivo de log para adjuntar
		log_file = self.__make_temp_log_file(context)
		
		mailer.send_mail(
						to_addr		= self.__to,
						msg			= msg,
						subject		= subject,
						from_addr	= 'Reporte SDF',
                   		from_header	= 'Reporte SDF',
                   		attach_files = [ (log_file, "log.txt") ]
						)    
		
		remove(log_file) # borra el archivo temporal	
		
		mailer.close()
	
	
	
	
	__mail_message_template = """
	<tr style="color: $message_color;">
	<td style="vertical-align: top;"><pre style="margin: 0px">[$date]</pre></td>
	<td style="vertical-align: top;"><pre style="margin: 0px">$message</pre></td>
	<tr>
	"""
		
	__mail_template_html = """
	<html>
	<body>
		<table width="100%">
		<tr><td style="background-color: $title_color; color: white;
				font-size: 1.2em; font-weight: bold; padding: 3px;">
			El parser <code>$parser</code> $project terminó $res
		</td></tr>
		<tr><td>
			<ul>
				<li><b>Hora de inicio</b>: $start (hora local)</li>
				<li><b>Hora de fin</b>: $end (hora local)</li>	
			</ul>		
		</td></tr>
		<tr><td>A continuación se muestra las últimas líneas de
				la salida
		</td></tr>
		<tr><td></td></tr>
		<tr><td><table cellspacing=0>
			$messages
		</table></td></tr>
		</table>
	</body>
	</html>
	"""  