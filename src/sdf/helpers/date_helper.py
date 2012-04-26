# *- encoding: utf-8 -*
'''
Created on 10/02/2010

@author: ignacio
'''
import re
from datetime import datetime
from sdf.util.typecheck import check_if_any_type

class DateHelper(object):
	"Implementa funciones de manejo de fechas"
	
	__months = {
			"ene": 1,
			"jan": 1,
			"gen": 1,
			"feb": 2,
			"fev": 2,
			"f\x00e9v": 2,
			"mar": 3,
			"maa": 3,
			"m\x00e4r": 3,
			"abr": 4,
			"apr": 4,
			"avr": 4,
			"may": 5,
			"mai": 5,
			"mei": 5,
			"jun": 6,
			"juin": 6,
			"jul": 7,
			"juil": 7,
			"ago": 8,
			"ao\x00fb": 8,
			"aou": 8,
			"aug": 8,
			"set": 9,
			"sep": 9,
			"oct": 10,
			"okt": 10,
			"nov": 11,
			"dic": 12,
			"dec": 12,
			"des": 12,
			"dez": 12,
			"d\x00e9c": 12
	}

	@staticmethod		
	def __get_month(month):
		"Devuelve el mes según la lista en self.__months"
		if re.search('\d+', month) != None:
			return int(month)
		month = month.strip()
		monthNum = DateHelper.__months.get(month[0:3])
		if monthNum == None:
			monthNum = DateHelper.__months.get(month[0:4])
		if monthNum == None:
			raise ValueError("Invalid month: %s" % month)
		else:
			return monthNum

	@staticmethod
	def __create_pattern(text):
		res = ''
		start_idx = 0
		
		day_match_idx = 0
		month_match_idx = 0
		year_match_idx = 0
		
		for match in re.finditer('(\s+|<\*>|<d>|<m>|<y>)', text, re.I | re.M | re.S | re.U):
			res += re.escape(text[start_idx:match.start()])
			if match.group() == "<d>":
				res += '(?P<day%d>\w+)' % day_match_idx
				day_match_idx += 1
			elif match.group() == "<m>":
				res += '(?P<month%d>\w+)' % month_match_idx
				month_match_idx += 1
			elif match.group() == "<y>":
				res += '(?P<year%d>\w+)' % year_match_idx
				year_match_idx += 1
			elif match.group() == "<*>":
				res += '.+'
			else:
				res += '\s+'
			
			start_idx = match.end()
			
		return '^' + res + re.escape(text[start_idx:]) + '$'
	
	@staticmethod
	def parse(date_str, patterns, default_year = None):
		"""
		Parsea una fecha según patrones dados y retorna un objeto de tipo
		datetime.
		Los patrones pueden tener tener los siguientes contenidos
		<m> coincide con el mes (su nombre o su representación numérica)
		<y> coincide con el año (un número)
		<d> coincide con el día (un número)
		<*> coincide con espacios
		los otros caracteres se toman como tales
		
		Un ejemplo es :: 
	
			patterns = '<d> de <m> del <y>'
			DateHelper.parse_range('3 de septiembre del 2010', patterns)
			
		devuelve un objeto *datetime* con el valor 3/9/2010
		"""
		check_if_any_type(date_str, [str, str])
		
		
		if isinstance(patterns, str) or isinstance(patterns, str):
			patterns = [ patterns ]
		if len(patterns) == 0:
			raise ValueError("At least one pattern must be defined")

		if default_year == None:
			default_year = datetime.now().year
			
		for pattern in patterns:
			pattern = DateHelper.__create_pattern(pattern)
			match = re.search(pattern, date_str, re.S | re.M | re.I)
			if not match:
				continue
			
			groups = match.groupdict()
			day, month, year = DateHelper.__prepare_day_month_year(groups['day0'],
									groups['month0'], groups.get('year0'),
									default_year)
				
			return datetime(year, month, day)

		else:
			raise ValueError("Invalid date: " + date_str)

	@staticmethod
	def parse_range(date_str, patterns, default_year = None):
		"""
		Igual que :func:`parse` pero parsea una fecha que comprenda un
		rango de dos fechas,
		
		Ejemplo ::
		
			patterns = '<d> al <d> de <m> del <y>'
			DateHelper.parse_range('3 al 4 de septiembre del 2010', patterns)
			
		devuelve una lista de objetos *datetime* con valores 
		[ 3/9/2010, 4/9/2010 ]
			
		"""
		check_if_any_type(date_str, [str, str])
		
		if isinstance(patterns, str) or isinstance(patterns, str):
			patterns = [ patterns ]
		if len(patterns) == 0:
			raise ValueError("At least one pattern must be defined")

		if default_year == None:
			default_year = datetime.now().year
			
		for pattern in patterns:
			pattern = DateHelper.__create_pattern(pattern)
			match = re.search(pattern, date_str, re.S | re.M | re.I)
			if not match:
				continue
			
			groups = match.groupdict()
			day0 = groups['day0']
			day1 = groups.get('day1', day0)
			month0 = groups['month0']
			month1 = groups.get('month1', month0)
			year0 = groups.get('year0')
			year1 = groups.get('year1', year0)
			
			day0, month0, year0 = DateHelper.__prepare_day_month_year(
					day0, month0, year0, default_year)
			day1, month1, year1 = DateHelper.__prepare_day_month_year(
					day1, month1, year1, default_year)
			
			return (
					datetime(year0, month0, day0),
					datetime(year1, month1, day1)
				)
		else:
			raise ValueError("Invalid date: " + date_str)



	@staticmethod
	def __prepare_day_month_year(day, month, year, default_year):
		if year is None:
			year = default_year
		else:
			year = int(re.compile('[^\d]+', re.U).sub('', year))
			if year < 100:
				year += 2000
		
		month = DateHelper.__get_month(month.strip())
		day = int(re.compile('[^\d]+', re.U).sub( '', day))
		
		return (day, month, year)