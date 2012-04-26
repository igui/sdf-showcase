# *- encoding: utf-8 -*
import re
from sdf.util.typecheck import check_if_any_type

class TextHelper(object):
	
	def __init__(self, context):
		self.context = context
		self.__extract_html_comments = re.compile(
			"(?:<!--(?:.|[\r\n])*?-->)", re.U)
		
		self.__extract_html_head = re.compile(
			"(?:<head\s*.*?>(?:.|[\r\n])*?</head>)", re.U)
		
		self.__extract_html_scripts = re.compile(
			"(?:<script\s*.*?>(?:.|[\r\n])*?</script>)" +
			"|(?:<script\s*(?:.|[\r\n])*?/>)", re.U)
		
		self.__extract_html_tag_attributes1 = re.compile(
			"<([a-z]+)\s+([^>]+)/>", re.U)
		
		self.__extract_html_tag_attributes2 = re.compile(
			"<([a-z]+)\s+([^>]+)>", re.U)
		
		self.__replace_html_comments = ""
		self.__replace_html_head = ""
		self.__replace_html_scripts = ""
		self.__replace_tag_attributes1 = "<\g<1>/>"
		self.__replace_tag_attributes2 = "<\g<1>>"
		self.__re_tabs = re.compile("\t")
		self.__re_enters = re.compile("\n")
		self.__re_enters2 = re.compile("\r")
		self.__re_whitespaces = re.compile(" {2,}")


	def clean_html(self, text):
		"""
		Limpia un código HTML, realizando los siguientes pasos
		
		#. borra comentarios HTML <!-- -->
		#. borra el cabezal <head></head>
		#. borra los elementos <script></script>
		#. borra los atributos del html
		
		Por ejemplo ::
		
			html = \"""
				<html>
				<head><title>Algo</title></head>
				<body><div name="limpiame">Texto del div</div>
				<script type="javascript">var a = 1</script>
				</body></html> 
			\"""
			print self.text_helper.clean_html(html)
		
		Da como resultado
		
		.. code-block:: html
		
			<html>
			
			<body><div>Texto del div</div>
			
			</body></html> 
			
		"""
		check_if_any_type(text, [str, str])
		
		text = self.__extract_html_comments.sub(
										self.__replace_html_comments, text)
		text = self.__extract_html_head.sub(self.__replace_html_head, text)
		text = self.__extract_html_scripts.sub(
											self.__replace_html_scripts, text)
		text = self.__extract_html_tag_attributes1.sub(
										self.__replace_tag_attributes1, text)
		text = self.__extract_html_tag_attributes2.sub(
										self.__replace_tag_attributes2, text)
		return text

	def remove_all_html_tags(self, text):
		"""
		Igual que :func:`remove_html_tags` pero saca todos los tags HTML
		"""
		check_if_any_type(text, [str, str])
		
		text = re.compile('<\/?.*?\/?>', re.U).sub('', text)		
		return text
	
	def remove_html_tags(self, text, tags):
		"""
		Saca todos los tags indicados html indicados del texto. Reemplaza cada 
		ocurrencia de un elemento que tiene los tags por el texto que contiene		
		"""
		check_if_any_type(text, [str, str])

		for tag in tags:
			check_if_any_type(tag, [str, str])
			text = re.compile('<\/?%s\/?>'  % tag, re.U).sub('', text)
		return text
	
	def clean_text(self, text, delete_enters=True):
		"""
		Quita todos los ``'\\r'`` de un texto, todos los espacios en blanco
		repetidos, todos las tabulaciones. Si *delete_enters* es **True** 
		también borra todos los ``'\\n'`` 
		"""
		check_if_any_type(text, [str, str])
		
		text = self.__re_enters2.sub('', text)
		if (delete_enters) :
			text = self.__re_enters.sub(' ', text)
		else:
			text = self.__re_enters.sub('\n', text) 
		text = self.__re_tabs.sub('', text)
		text = self.__re_whitespaces.sub(' ', text)
		text = text.strip()
		return text
