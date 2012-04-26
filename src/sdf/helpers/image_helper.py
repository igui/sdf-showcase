# *- encoding: utf-8 -*

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

import io
import subprocess
import sys
import os
import tempfile
from urllib.request import urlretrieve

try:
	import Image
	import ImageEnhance
except ImportError:
	msg = 'Se necesitan las dependencias: tesseract-ocr y PIL para usar el ImageHelper. Visitar '
	msg += '"http://code.google.com/p/tesseract-ocr/"'
	msg += ', "http://www.pythonware.com/products/pil/"'	
	raise ImportError(msg)

class ImageHelper(object):
	
	def __init__(self, context):
		self.context = context	
	
	def __run_tesseract(self, input_filename, output_filename_base, lang=None, permited_chars_file=None):
		'''
		runs the command:
			`tesseract_cmd` `input_filename` `output_filename_base`
	
		returns the exit status of tesseract, as well as tesseract's stderr output	
		'''
	
		command = [tesseract_cmd, input_filename, output_filename_base]
		# Utilizar experiencia de un lenguaje particular.
		if lang is not None:
			command += ['-l', lang]	
		# Reconocer solo algunos caracteres
		if permited_chars_file is not None:
			command += ['nobatch', permited_chars_file]	
	
		proc = subprocess.Popen(command, stderr=subprocess.PIPE)
		return (proc.wait(), proc.stderr.read())
	
	def __cleanup(self, filename):
		''' tries to remove the given filename. Ignores non-existent files '''
		try:
			os.remove(filename)
		except OSError:
			pass
	
	def __get_errors(self, error_string):
		'''
	    returns all lines in the error_string that start with the string "error"	
	    '''
	
		lines = error_string.splitlines()
		error_lines = (line for line in lines if line.find('Error') >= 0)
		return '\n'.join(error_lines)
	
	def __tempnam(self):
		''' returns a temporary file-name '''
	
		# prevent os.tmpname from printing an error...
		stderr = sys.stderr
		try:
			sys.stderr = io.StringIO()
			return os.tempnam(None, 'tess_')
		finally:
			sys.stderr = stderr
	
	def __image_to_string(self, image, lang=None, permited_chars=None):
		'''
		Runs tesseract on the specified image. First, the image is written to disk,
		and then the tesseract command is run on the image. Resseract's result is
		read, and the temporary files are erased.		
		'''
	
		input_file_name = '%s.bmp' % self.__tempnam()
		output_file_name_base = self.__tempnam()
		output_file_name = '%s.txt' % output_file_name_base
		permited_chars_file_name = None
		try:
			image.save(input_file_name)
			
			if permited_chars is not None and permited_chars != '':
				permited_chars_file_name = self.__tempnam()
				f_perm = open(permited_chars_file_name, 'w')
				f_perm.write("tessedit_char_whitelist " + permited_chars)
				f_perm.close()
			
			status, error_string = self.__run_tesseract(input_file_name,
													    output_file_name_base, lang=lang,
													     permited_chars_file=permited_chars_file_name)
			if status:
				errors = self.__get_errors(error_string)
				raise TesseractError(status, errors)
			f = file(output_file_name)
			try:
				return f.read().strip()
			finally:
				f.close()
		finally:
			self.__cleanup(input_file_name)
			self.__cleanup(output_file_name)
			if permited_chars_file_name is not None:
				self.__cleanup(permited_chars_file_name)
		
	def __get_text(self, image, scale=100, contrast=1.0, background=(255, 255, 255,), permited_chars=None):
		tfile = image
		try:
			if image.lower().split(':')[0] in ['http', 'file', 'https', 'ftp']:
				tfile_d,tfile = tempfile.mkstemp()
				
				# Abro y cierro el fd obtenido para no pasarme del limite de archivos abiertos.
				tfile_p=os.fdopen(tfile_d,'w')
				tfile_p.close()
				
				urlretrieve(image, tfile)
		except:			
			tfile = image
		timg = Image.open(tfile)
		w, h = timg.size
		#transparency
		if timg.mode == 'RGBA':
			background = Image.new('RGBA', timg.size, background)
			background.paste(timg, timg)
			timg = background.convert('RGB')
		elif timg.mode == 'P':
			pixels = []
			for x in range(w):
				for y in range(h):
					try:
						if timg.getpixel((x,y)) == timg.info['transparency']:
							pixels.append((x,y))
					except KeyError:
						# pixels.append((x,y)) ?
						continue
			bimg = Image.new('RGB', timg.size, background)		
			bimg.paste(timg, (0,0,w,h))
			timg = bimg
			for xy in pixels:
				timg.putpixel(xy, background)
		#constrast
		timg = ImageEnhance.Contrast(timg)
		timg = timg.enhance(contrast)
		#size
		w = (w * scale) / 100
		h = (h * scale) / 100
		timg = timg.resize((w, h), Image.NEAREST)
		return self.__image_to_string(timg, permited_chars=permited_chars)
	
	def get_text_from_image(self, image_url, scale=150, contrast=1.0, background=(255, 255, 255,), permited_chars=None):
		"""
		Recibe la url de una imagen que representa un texto y la somete a un proceso de OCR
		(Optical Character Recognition). Devuelve una cadena con la mejor aproximación al texto
		de la imagen.
		
		Se pueden ajustar los parámetros *scale* y *contrast* para lograr un mejor reconocimiento. Es
		útil además elegir un fondo con el parámetro *background* (en RGB) que contraste con el texto
		de la imagen. Por defecto se usa un fondo blanco.
		
		Además se cuenta con el parámetro *permited_chars* que permite especificar, en el caso de que se
		sepa de antemano, cuales son los caracteres que pueden aparecer en la imagen. De esta manera sólo
		se intenta detectar dichos caracteres mejorando mucho la precisión. 
		
		Un ejemplo ::
		
			from sdf.helpers.image_helper import ImageHelper
			
			# Cargo Google (ncr es para que si o si vaya a la pagina de USA)
			browser.load_page("http://www.google.com/ncr")
			# Obtengo la imagen con el logo
			logo = browser.find(tag = 'img', attribute = { 'alt' : 'Google' })
			# Obtengo el texto de la imagen y lo imprimo
			if logo is not None:
				print 'El texto del logo es:', ImageHelper(context).get_text_from_image(logo.src, permited_chars="aGbcoleg")
			
		En la consola deberíamos obtener ::
			
			El texto del logo es: Google
		"""
		return self.__get_text(image_url, scale, contrast, background, permited_chars=permited_chars)
	
class TesseractError(Exception):
		def __init__(self, status, message):
			self.status = status
			self.message = message
	