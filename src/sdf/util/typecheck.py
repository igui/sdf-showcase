# *- encoding: utf-8 -*
'''
Created on 24/02/2010

@author: iavas
'''

from .. import exception
from numbers import Integral

def check_if_any_subclass(value, types):
	"""
	Checkea si value es de algún tipo de types, si no lo es tira una excepción
	del tipo TypeError
	"""
	if isinstance(types, type):
		types = [ types ]
	elif len(types) == 0 or not hasattr(types, '__iter__'):
		raise exception.LogicError("non empty list was expected for types arg")
	
	for t in types:
		if issubclass(value, t):
			return
	
	if len(types) == 1:
		typenames_joined = types[0].__name__
	else:
		typenames = [ t.__name__ for t in types ]	
		typenames_joined = str.join(', ', typenames[:-1]) + ' or ' + \
			typenames[-1]
	
	error_msg = "%s expected but %s given"
	value_class_name = value.__class__.__name__
	raise TypeError(error_msg % (typenames_joined, value_class_name))


def check_if_any_type(value, types):
	"""
	Checkea si value es de algún tipo de types, si no lo es tira una excepción
	del tipo TypeError
	"""
	if isinstance(types, type):
		types = [ types ]
	elif len(types) == 0 or not hasattr(types, '__iter__'):
		raise exception.LogicError("non empty list was expected for types arg")
	
	for t in types:
		if t is None and value is None or t is not None and isinstance(value, t):
			return
	
	if len(types) == 1:
		typenames_joined = types[0].__name__
	else:
		typenames = [ t.__name__ for t in types ]	
		typenames_joined = str.join(', ', typenames[:-1]) + ' or ' + \
			typenames[-1]
	
	error_msg = "%s expected but %s given"
	value_class_name = value.__class__.__name__
	raise TypeError(error_msg % (typenames_joined, value_class_name))


def check_if_integral(value):
	"Checkea si el valor es int o long"
	check_if_any_type(value, Integral)
