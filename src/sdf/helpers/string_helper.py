# -*- coding: utf-8 -*-

import re
import cgi
import html.entities
from sdf.util.typecheck import check_if_any_type

class StringHelper(object):

	@staticmethod 
	def escape_html(string):
		return cgi.escape(string)

	@staticmethod
	def _char_unescape(m, defs=html.entities.entitydefs):
		try:
			return defs[m.group(1)]
		except KeyError:
			return m.group(0)

	@staticmethod
	def unescape_html(string):
		_char = re.compile(r'&(\w+?);', re.U)
		_dec  = re.compile(r'&#(\d{2,4});', re.U)
		_hex  = re.compile(r'&#x(\d{2,4});', re.U)
		result = _hex.sub(lambda x: chr(int(x.group(1), 16)),\
			_dec.sub(lambda x: chr(int(x.group(1))),\
			   _char.sub(StringHelper._char_unescape, string)))
		return result
	
	@staticmethod
	def extract_all(pattern, text):
		return Extractor.extract_all(pattern, text)
	
	@staticmethod
	def extract(pattern, text):
		return Extractor.extract(pattern, text)
	
	@staticmethod
	def force_unicode(s, encoding='utf-8', errors='ignore'):
		"""
		-- Tomado del Framework Django --
		Returns a unicode object representing 's'. Treats bytestrings using the
		'encoding' codec.
		"""
		if s is None:
			return ''
		try:
			if not isinstance(s, str,):
				if hasattr(s, '__unicode__'):
					s = str(s)
				else:
					try:
						s = str(str(s), encoding, errors)
					except UnicodeEncodeError:
						if not isinstance(s, Exception):
							raise
						# If we get to here, the caller has passed in an Exception
						# subclass populated with non-ASCII data without special
						# handling to display as a string. We need to handle this
						# without raising a further exception. We do an
						# approximation to what the Exception's standard str()
						# output should be.
						s = ' '.join([StringHelper.force_unicode(arg, encoding, errors) for arg in s])
			elif not isinstance(s, str):
				# Note: We use .decode() here, instead of unicode(s, encoding,
				# errors), so that if s is a SafeString, it ends up being a
				# SafeUnicode at the end.
				s = s.decode(encoding, errors)
		except UnicodeDecodeError as e:
			if not isinstance(s, Exception):
				raise UnicodeDecodeError (s, *e.args)
			else:
				# If we get to here, the caller has passed in an Exception
				# subclass populated with non-ASCII bytestring data without a
				# working unicode method. Try to handle this without raising a
				# further exception by individually forcing the exception args
				# to unicode.
				s = ' '.join([StringHelper.force_unicode(arg, encoding, errors) for arg in s])
		return s
	
	###################### Métodos de StringExtensions ##########################
	
	### TODO Probaaar!
	
	@staticmethod
	def cut(text, length, postfix):
		"""
		Corta un string y le deja hasta length caracteres y si se pasa le concatena el 
		postfijo dado
		"""
		if len(text) <= length:
			return text;
		if length < len(postfix):
			return postfix[0: length]

		p = text.rfind(' ', 0, length - len(postfix))
		if p == -1:
			p = length - len(postfix)
		
		return text[0:p] + postfix
	
	@staticmethod
	def clean(text, *old_values):
		for si in old_values:
			text = text.replace(si, "");
		return text;
	
	@staticmethod
	def clear_attributes_replace(match):
		pre = match.group(1)
		if pre == None:
			pre = ''
		post = match.group(4)
		if post == None:
			post = ''
		return "<%s%s%s>" % (pre, match.group(2).lower(), post)
	
	@staticmethod
	def clear_attributes(text):
		attr_pattern = re.compile('<(/)?([a-z]+)([^>]+)?(/)?>',
			re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
		return attr_pattern.sub(StringHelper.clear_attributes_replace, text)
	
	@staticmethod
	def clear_tags(text, *tags):
		if len(tags) == 0:
			pattern = re.compile('<\/?\w+\/?>|<\/?\w+\s*[^>]*?\/?>',
				re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
			return pattern.sub(" ", text)
		else:
			for tag in tags:
				pattern = re.compile('<\/?%s\/?>|<\/?%s\s*[^>]*?\/?>' %
					(tag, tag),
					re.DOTALL | re.MULTILINE | re.IGNORECASE | re.UNICODE)
				text = pattern.sub(" ", text)
			return text
		
	@staticmethod
	def remove_control_chars(s):
		control_chars = ''.join(map(chr, list(range(0,32)) + list(range(127,160))))
		# saca los que si se quieren imprimir
		control_chars = control_chars.replace('\n', '')
		control_chars = control_chars.replace('\r', '')
		control_chars = control_chars.replace('\t', '')
		control_char_re = re.compile('[%s]' % re.escape(control_chars))
	
		return control_char_re.sub('', s)
		
	
extractor_cache = {}
extractor_special = dict.fromkeys( r'.^$*+?{}[]\|()', 1)

class Extractor(object):

	@staticmethod
	def __escape(pattern):
		holder = list(pattern)
		for i, c in enumerate(pattern):
			if c in extractor_special:
				holder[i] = "\\%c" % (c)
			elif c == "\000":
				holder[i] = "\\000"
		return ''.join(holder)
	
	@staticmethod
	def __create_pattern(text):
		if text in extractor_cache:
			return extractor_cache[text]
		pattern = ''
		p = 0
		prev_char = None
		context = 0 #0=text, 1=open tag, 2=close tag
		tag_context = 0 #0=espacio, 1=text
		in_value = False
		value_stop = None
		in_re = False
		
		while p < len(text):
			char = text[p]
			next_char = text[p+1:p+2] 
			n_prev_char = char
			n_p = p + 1
			
			if char == '#' and prev_char != '\\':
				if context == 0:
					pattern += '(?P<content>.*?)'
				elif context == 1 or context == 2:
					if in_value:
						pattern += '(?P<content>[^%s]*?)' % value_stop
					else:
						pattern += '(?P<content>[^>]*?)'
			elif char == '%' and prev_char  != '\\':
				in_re = not in_re
				if in_re and context == 1:
					tag_context = 1
				elif not in_re and context == 1:
					tag_context = 0
			elif in_re:
				pattern += char
				
			#in text
			elif context == 0:
				if char == ' ': #text
					pattern += '\s+?'
				elif char == '<' and next_char == '/': #close tag
					context = 2
					tag_context = 0
					pattern += '\s*?</'
					n_prev_char = '/'
					n_p += 1
				elif char == '<': #open tag
					context = 1
					tag_context = 0
					pattern += '\s*?<'
				elif char == '#' and prev_char == '\\':
					pattern = pattern[:-1] + char
				else:
					pattern += Extractor.__escape(char)
			
			#in tag
			elif context == 1 or context == 2:
				if in_value:
					if char == value_stop:
						value_stop = None
						in_value = False
						pattern += Extractor.__escape(char)
					else:
						pattern += Extractor.__escape(char)
				else:
					if tag_context == 0:
						if char != ' ':
							tag_context = 1
						elif char == ' ':
							pattern += '[^>]+?'
					if tag_context == 1:
						if char == '=':
							pattern += "\s*=\s*"
						elif char == '"':
							value_stop = '"'
							in_value = True
							pattern += Extractor.__escape(char)
						elif char == "'":
							value_stop = "'"
							in_value = True
							pattern += Extractor.__escape(char)
						elif char == '/' and next_char == '>':
							context = 0
							pattern += '[^>]*?/>\s*?'
							n_prev_char = '>'
							n_p += 1
						elif char == '>':
							context = 0
							pattern += '[^>]*?>\s*?'
						elif char != ' ':
							pattern += Extractor.__escape(char)
						elif char == ' ':
							tag_context = 0
							pattern += '[^>]+?'
							
			prev_char = n_prev_char
			p = n_p
		while pattern.startswith('\s*?'):
			pattern = pattern[4:]
		while pattern.endswith('\s*?'):
			pattern = pattern[:-4]
		pattern = re.sub('(?:\.\*\?)(?:\.\*\?)+', '.*?', pattern)
		pattern = re.sub('(?:\.\*)(?:\.\*)+', '.*', pattern)
		pattern = re.sub('(?:\.\+\?)(?:\.\+\?)+', '.+?', pattern)
		pattern = re.sub('(?:\.\+)(?:\.\+)+', '.+', pattern)
		pattern = re.sub('(?:\\\s\+\?)(?:\\\s\+\?)+', '\s+?', pattern)
		pattern = re.sub('(?:\\\s\+)(?:\\\s\+)+', '\s+', pattern)
		pattern = re.sub('(?:\\\s\*\?)(?:\\\s\*\?)+', '\s*?', pattern)
		pattern = re.sub('(?:\\\s\*)(?:\\\s\*)+', '\s*', pattern)
		pattern = re.sub('(?:\[\^\>\]\+\?)(?:\[\^\>\]\+\?)+', '[^>]+?', pattern)
		pattern = re.sub('(?:\.\*\?)*\(\?P<content>\.\*\?\)(?:\.\*\?)*', '(?P<content>.*?)', pattern)
		pattern = re.sub('(?:\\s\*\?)*\(\?P<content>\.\*\?\)(?:\\s\*\?)*', '(?P<content>.*?)', pattern)
		pattern = re.sub('</([a-zA-Z]+)\[\^\>\]\*\?>', '</\g<1>>', pattern)
		extractor_cache[text] = pattern
		return pattern
	
	@staticmethod
	def extract_all(pattern, text):
		"""
		Extrae de text usando un patrón de reglas complejas orientadas a HTML
		pattern denota una expresión regular que cumple las siguientes reglas:
				
		- El caracter ``'#'`` coincide con cualquier contenido.
			En su forma exacta
			``#`` coincide con la expresión regular clásica ``\s*?(.*?)\s*?``
		
		- El ``%foobar%`` coincide con la expresión regular clásica foobar,
			esto sirve para hacer coincidir con una expresión regular clásica.
			Por ejemplo el pattern ``'%\\\\bA\\\\w*\\\\b%'``
			coincide con todas las palabras que empiecen con A mayúscula
		
		- Las expresiones del tipo <foo><bar> ignoran los posibles atributos 
		  de los elementos, son equivalentes a la expresión regular
		  ``<foo[^>]*?>\s*?<bar[^>]*?>``
		  
		extract_all devuelve una lista de todas las coincidencias de #, según
		las reglas anteriores, buscando en el string text
		
		Ejemplo::
			
			t = "<div class="t"> <a href="/"> foo </a> <a> bar</a> </div>
			
			extract_all('<a>#</a>', t)      # devuelve [ 'foo', 'bar' ]
			extract_all('<div><a>#</a>', t) # devuelve [ 'foo' ]
			extract_all('#</a></div>'       # devuelve [ 'bar' ]
		"""
		list = []
		pattern = Extractor.__create_pattern(pattern)
		for f in re.finditer(pattern, text, re.DOTALL | re.UNICODE | re.IGNORECASE):
			list.append(f.group('content'))
		return list
	
	@staticmethod
	def extract(pattern, text):
		"""
		Igual que :func:`extract_all` pero devuelve la primera ocurrencia
		o None si no se encuentra ninguna
		"""
		pattern = Extractor.__create_pattern(pattern)
		f = re.search(pattern, text, re.DOTALL | re.UNICODE | re.IGNORECASE)
		if f is not None:
			return f.group('content')
		return None
	
	@staticmethod
	def make_sentence(text):
		"""
		Cambia el texto a formato de oración: Cambia todas los tokens
		delimitados por *'.'* o *'\\\\n'* a Mayuscula minuscula
		"""
		check_if_any_type(text, [str, str])
		
		i = 0
		while True:
			while i < len(text) and not text[i].isalpha():
				i+=1
			if i >= len(text):
				break

			text[i] = text[i].upper()
				
			while i < len(text):
				if text[i] in ".\n":
					i+=1
					break
				else:
					text[i].lower()
					i+=1
		
		return text
		
