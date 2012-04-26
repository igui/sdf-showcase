import sdf 
from .data_adapter_xml import DataAdapterXML

class Options(sdf.options.Options):
	def __init__(self):
		sdf.options.Options.__init__(self)
		self.data_adapter_class = DataAdapterXML 
		self.output_file = "videos.xml"
