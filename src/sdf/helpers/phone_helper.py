# *- encoding: utf-8 -*

import re
from sdf.util import deprecated

class PhoneHelper(object):
	
	def __init__(self, context):
		self.context = context
		self.__re_replace_separators = re.compile('[-\t\x20\.\\\/]+', re.U)
		self.__re_replace_zero = re.compile('\(0\)', re.U)
		self.__re_replace_parenthesis = re.compile('[\(\)]+', re.U)
		self.__re_replace_all = re.compile("[^0-9]+", re.U)
		
		self.__re_phones = re.compile('[\d\-\./\\\x20\t+()]+', re.U)
		self.__re_number = re.compile('\d', re.U)
		self.__re_spaces = re.compile('[\x20\t]+', re.U)
		
		self.__tags = ('a,em,strong,q,cite,dfn,abbr,acronym,sub,sup,big,' + \
				'small,b,i,font,u').split(',')


	def __format(self, phone, countries):
		phone = phone.strip()
		phone = self.__re_replace_separators.sub('', phone)
		phone = self.__re_replace_zero.sub('', phone)
		phone = self.__re_replace_parenthesis.sub('', phone)

		if phone.startswith("+00"):
			phone = phone[1:]
		elif phone.startswith("+"):
			phone = "00" + phone[1:]

		while phone.startswith("000"):
			phone = phone[1:]

		phone_country = None
		if not phone.startswith("00"):
			fphone = None
			for country in countries:
				default_country = self.context.countries[country]
				tphone = phone
				#En italia los prefijos de ciudad igual llevan 0 adelante cuando se les pone 0039
				#fuente: http://www.bluhome.it/page.aspx?ID=d5d8c8d34f3448b18ee7a18191c196c4&lng=es-ES
				if not default_country.phone_landline_zero_prefix and tphone.startswith("0"):
					tphone = tphone[1:]
				tphone = default_country.phone_international_prefix + tphone
				if fphone is None: fphone = tphone
				phone_country = self.context.countries.get_by_phone(tphone)
				if phone_country is not None and phone_country.is_valid_phone(tphone):
					fphone = tphone
					break
				else:
					tphone = '00' + phone
					phone_country = self.context.countries.get_by_phone(tphone)
					if phone_country is not None and phone_country.is_valid_phone(tphone):
						fphone = tphone
						break
			phone = fphone
		else:		
			phone_country = self.context.countries.get_by_phone(phone)	
		
		if phone_country is not None:
			if not phone_country.phone_landline_zero_prefix and phone.startswith(phone_country.phone_international_prefix + "0"):
				phone = phone_country.phone_international_prefix + phone[len(phone_country.phone_international_prefix) + 1:]
		else:
			for country in countries:
				phone_country = self.context.countries[country]
				if not phone_country.phone_landline_zero_prefix and phone.startswith(phone_country.phone_international_prefix + "0"):
					phone = phone_country.phone_international_prefix + phone[len(phone_country.phone_international_prefix) + 1:]
					break
		phone = self.__re_replace_all.sub('', phone);
		return phone
	
	def __is_valid_landline(self, phone):
		country = self.context.countries.get_by_phone(phone)
		if country is not None and country.is_valid_landline_phone(phone):
			return True
		return False

	def __is_valid_mobile(self, phone):
		country = self.context.countries.get_by_phone(phone)
		if country is not None and country.is_valid_mobile_phone(phone):
			return True
		return False
	
	def __is_valid_fax(self, phone):
		country = self.context.countries.get_by_phone(phone)
		if country is not None and country.is_valid_fax_phone(phone):
			return True
		return False
	
	def __get_phones(self, text):
		all_phones = self.__extract_phones(text)
		all_phones.sort()
		phones = []
		for phone in all_phones:
			if phone not in phones:
				phones.append(phone)
		return phones
		
	def __extract_phones(self, text):
		phones = []
		for phones_m in self.__re_phones.finditer(text):
			text = phones_m.group(0)
			if len(self.__re_number.findall(text)) <= 7:
				continue
			text = text.lstrip('-,./\\\x20\t\)').rstrip('-,./\\\x20\t\(')
			text = re.sub('\(.*?\)',
					lambda m: self.__re_spaces.sub('', m.group(0)), text)
			tphones = text.split('+')
			tphones = [
					tphone.lstrip('-,./\\\x20\t\)').rstrip('-,./\\\x20\t\(')
						for tphone in tphones]
			if len(tphones) > 1:
				tphones = [
					'+' + re.compile('^([^()]+)\)[\x20\t]*', re.U).sub(
						'\g<1>' , tphone) for tphone in tphones
					]
			tphones = [x for x in tphones if x != '+']
			if len(tphones) > 1:
				for tphone in tphones:
					phones += self.__extract_phones(tphone)
			else:
				text = tphones[0]
				tseparators = {}
				for tseparator_m in re.compile('[^\d]+').finditer(text):
					key = tseparator_m.group(0)
					if key not in tseparators:
						tseparators[key] = 1
					else:
						tseparators[key] += 1					
				separators = {}
				for tseparator, ttotal in list(tseparators.items()):
					ts = text.split(tseparator)
					add = True
					for t in ts:
						if len(re.findall(r'\d', t)) <= 7:
							add = False
					if add:
						separators[tseparator] = ttotal
				if len(separators) > 0:
					for separator in separators:
						ts = text.split(separator)
						ts = [re.compile('^([^()]+)\)[\x20\t]*', re.U).
							sub('\g<1>' , t) for t in ts ]
						for t in ts:
							phones += self.__extract_phones(t)
				else:
					phones.append(text)
		return phones
	
	def __prepare_text(self, text):
		return self.context.text_helper.remove_html_tags(
			self.context.text_helper.clean_html(text), self.__tags)
	
	def __call_fill(self, f, text, item, exclude, countries):
		if exclude is None: exclude = []
		if countries is None: countries = []
		if isinstance(text, list):
			for t in text:
				f(self.__prepare_text(t), item, exclude, countries)
		elif isinstance(text, dict):
			for k, t in list(text.items()):
				f(self.__prepare_text(t), item, exclude, countries)
		else:
			f(self.__prepare_text(text), item, exclude, countries)
	
	@deprecated
	def fill(self, type, text, item, exclude=None, countries=None):
		self.__call_fill(self.__fill, text, item, exclude, countries)
	
	def __fill(self, text, item, exclude, countries):
		if len(countries) == 0:
			countries.append(item.country)
		for phone in self.__get_phones(text):
			phone = self.__format(phone, countries)
			if phone in exclude:
				continue
			if self.__is_valid_mobile(phone):
				if phone not in item.mobile_phones:
					item.mobile_phones.append(phone)
			elif self.__is_valid_landline(phone):
				if phone not in item.landline_phones:
					item.landline_phones.append(phone)
			else:
				item.has_invalid_data = True
				if phone not in item.landline_phones:
					item.landline_phones.append(phone)
	
	def extract_phones(self, text, countries, exclude = None, fallback = False):
		"""
		Extrae todos los teléfonos de un texto, y los devuelve en un objeto que
		tiene como atributos:
		
		* *landline_phones* que tiene los números de línea comunes
		* *mobile_phones* conteniendo los teléfonos móbiles
		* *fax_phones* que contiene los faxes
		* *all* que contiene una lista con todos los demás juntos 
			
		Por ejemplo, en un parser se puede hacer lo siguiente::
		
			text = \"\"\"
				Los teléfonos en uruguay son 02 622 22 33, 024087679 o
				móviles como 099 543 212
			\"\"\"
			phones = self.phone_helper.extract_phones(text, [ \'uy\' ])
			
			print "phones:           ", phones
			print "all:              ", phones.all 
			print "landline_phones:  ", phones.landline_phones
			print "mobile_phones:    ", phones.mobile_phones
			print "fax_phones:       ", phones.fax_phones
			
		Que da como resultado ::
			
			phones:            ExtractPhonesResult[ landline_phones: [u'0059826222233', u'0059824087679'] mobile_phones: [u'0059899543212'] fax_phones: [] ]
			all:               [u'0059826222233', u'0059824087679', u'0059899543212']
			landline_phones:   [u'0059826222233', u'0059824087679']
			mobile_phones:     [u'0059899543212']
			fax_phones:        []
		
		"""
		
		class PhoneHelperFillRes:
			def __init__(self):
				self.landline_phones = []
				self.mobile_phones = []
				self.fax_phones = []
				self.has_invalid_data = False

		if not countries:
			raise ValueError("countries must be a non empty list")
		elif isinstance(countries, str) or isinstance(countries, str):
			countries = [ countries ]

		i = PhoneHelperFillRes()
		self.__call_fill(self.__fill, text, i, exclude, countries)
		
		class ExtractPhonesObjRes:
			def __init__(self, mobile_phones, fax_phones, landline_phones):
				self.__landline_phones = landline_phones
				self.__mobile_phones = mobile_phones
				self.__fax_phones = fax_phones
				self.__list = landline_phones + mobile_phones + fax_phones
				
			@property
			def landline_phones(self):
				return self.__landline_phones
			
			@property
			def fax_phones(self):
				return self.__fax_phones
			@property
			def mobile_phones(self):
				return self.__mobile_phones
			
			@property
			def all(self):
				return self.__landline_phones + self.__mobile_phones + self.__fax_phones
				
			def __repr__(self):
				return ("ExtractPhonesResult[ landline_phones: %s mobile_phones: %s " + 
					"fax_phones: %s ]") % ( self.landline_phones,
						self.mobile_phones, self.fax_phones)
					
			def __iter__(self):
				return self.__list.__iter__()
	
			def __getitem__(self, i):
				return self.__list.__getitem__(i)

			def __len__(self):
				return len(self.__list) 

		# si fallback es True y no se extrajo ningún teléfono, se devuelve la
		# lista original
		if fallback and not i.landline_phones and not i.fax_phones and not i.mobile_phones:
			return ExtractPhonesObjRes([text], [], [])
		else:
			return ExtractPhonesObjRes(i.mobile_phones, i.fax_phones, i.landline_phones)

	
	@deprecated
	def fill_landlines(self, type, text, item, exclude=None, countries=None):
		self.__call_fill(self.__fill_landlines, text, item, exclude, countries)
		
	def __fill_landlines(self, text, item, exclude, countries):
		if len(countries) == 0:
			countries.append(item.country)
		for phone in self.__get_phones(text):
			phone = self.__format(phone, countries)
			if phone in exclude:
				continue
			if self.__is_valid_landline(phone):
				if phone not in item.landline_phones:
					item.landline_phones.append(phone)
			else:
				item.has_invalid_data = True
				if phone not in item.landline_phones:
					item.landline_phones.append(phone)

	@deprecated
	def fill_mobiles(self, type, text, item, exclude=None, countries=None):
		self.__call_fill(self.__fill_mobiles, text, item, exclude, countries)
		
	def __fill_mobiles(self, text, item, exclude, countries):
		if len(countries) == 0:
			countries.append(item.country)
		for phone in self.__get_phones(text):
			phone = self.__format(phone, countries)
			if phone in exclude:
				continue
			if self.__is_valid_mobile(phone):
				if phone not in item.mobile_phones:
					item.mobile_phones.append(phone)
			else:
				item.has_invalid_data = True
				if phone not in item.mobile_phones:
					item.mobile_phones.append(phone)
	
	@deprecated
	def fill_faxes(self, type, text, item, exclude=None, countries=None):
		self.__call_fill(self.__fill_faxes, text, item, exclude, countries)
		
	def __fill_faxes(self, text, item, exclude, countries):
		if len(countries) == 0:
			countries.append(item.country)
		for phone in self.__get_phones(text):
			phone = self.__format(phone, countries)
			if phone in exclude:
				continue
			if self.__is_valid_fax(phone):
				if phone not in item.fax_phones:
					item.fax_phones.append(phone)
			else:
				item.has_invalid_data = True
				if phone not in item.fax_phones:
					item.fax_phones.append(phone)
