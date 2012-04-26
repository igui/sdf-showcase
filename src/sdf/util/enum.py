from sdf.util.typecheck import check_if_any_type

def Enum(*names, **namevals):
	"""
	Representa una clase de enumerados
	
	algunos ejemplos son:
	e = Enum('a', 'b', 'c')
	e = Enum('a', 'b', c = 2)
	
	e = Enum(
			'a',
			b = 1,
			c = 2,
			d = 1,
			effa = 0
			)
	
	e = Enum(
			eggs = 0,
			ham = 1,
			spam = 2,
			nuts = 45
	)
	
	"""
	assert names or namevals, "Empty enums are not supported"
	
	enum_type = _EnumClass() 
	
	for i, each in enumerate(names):
		check_if_any_type(each, str)
		enum_type._add_value(each, i)
		
	for enum_name, enum_val in list(namevals.items()):
		enum_type._add_value(enum_name, enum_val)
		
	return enum_type

class _EnumClass(object):
	def __init__(self):
		self.__constants = {}
	
	def _add_value(self, name, value):
		enum_value = _EnumValue(self, name, value)
		
		if name not in self.__constants:
			self.__constants[name] = [ enum_value ]
			self.__setattr__(name, value)
		else:
			self.__constants[name].append(enum_value)
	
	@property
	def constants(self):
		"Retorna las constantes en una lista (numero->valor)"
		return  [ 
				(str(values[0]), name)
				for name, values in list(self.__constants.items())
				]
		
	def get_name(self, value):
		"Da el nombre de un enumerado con el valor buscado"
		for val in list(self.__constants.values()):
			if val[0].value == value:
				return val[0].name
		raise ValueError("No constant for value")
	
	def __iter__(self):
		return iter(self.__constants)
	
	def __len__(self):
		return len(self.__constants)
	
	def __getitem__(self, i):
		return self.__constants[i][0]
	
	def __repr__(self):
		return 'Enum' + str(self.__constants)
	
	def __str__(self):
		return 'enum ' + str(self.__constants)

class _EnumValue(object):
	def __init__(self, enum_type , name, value):
		self.__enum_type = enum_type
		self.__value = value
		self.__name = name
	
	@property
	def value(self):
		return self.__value
	
	@property
	def name(self):
		return self.__name
	
	@property
	def enum_type(self):
		return self.__enum_type
	
	def __hash__(self):
		return hash(self.__value)
	def __cmp__(self, other):
		if isinstance(other, _EnumValue):
			return cmp(self.__value, other.__value)
		else:
			return cmp(self.__value, other)
		
	def __bool__(self):
		return bool(self.__value)
	def __repr__(self):
		return str(self.__value)
	def __str__(self):
		return str(self.__value)
	