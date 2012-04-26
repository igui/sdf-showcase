# *- encoding: utf-8 -*

# Para que no joda lo del NoneType
import types
types.NoneType = None

# Chequea versión de python
import sys
if (sys.version_info.major, sys.version_info.minor) < (3,0):
	msg = "Se necesita Python 3.0 o superior"
	raise ImportError(msg)

# Chequea dependencias de paquetes externos 
try:
	import PyQt4 as __pyqt4_nothing
except ImportError:
	msg = 'Se necesita PyQt4. Visitar '
	msg += '"http://www.riverbankcomputing.co.uk/software/pyqt/download"'
	raise ImportError(msg)

try:
	import lxml as __lxml_nothing
except ImportError:
	msg = 'Se necesita lxml. Visitar '
	msg += '"http://pypi.python.org/pypi/lxml/2.3"'
	raise ImportError(msg)

try:
	import chardet as __chardet_nothing
except ImportError:
	msg = 'Se necesita el módulo chardet. Visitar '
	msg += '"http://chardet.feedparser.org/download/"'
	raise ImportError(msg)


# importaciones secundarias

from .parser_loader import ParserLoader
from .exception import LogicError, JavaScriptError, LoadPageError 
from .options import Options
from .state import State, ExecutionState
from .logger import Logger
from .properties import Properties
from .context import Context
from .data_adapter import DataAdapter
from .driver import Driver
from .base_parser import BaseParser
from .simple_parser import SimpleParser
from .item_manager import ItemManager
from .itemprocessorpipeline import ItemProcesorPipeline
from .list_based_parser import ListBasedParser
from .page_parser import PageParser
from .local_page_parser_driver import LocalPageParserDriver
from .page_parser_driver import BasePageParserDriver
from .redirect_writer import RedirectWriter
