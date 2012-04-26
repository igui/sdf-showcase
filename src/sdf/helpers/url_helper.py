import urllib.parse
import types
import urllib.request, urllib.parse, urllib.error
from PyQt4.QtCore import QUrl


class UrlHelper(object):
	
	def __init__(self, context):
		self.context = context
		
	def join(self, absolute, relative):
		if relative.startswith('?'):
			if absolute.find('?') != -1:
				relative = absolute[:absolute.find('?')] + relative
		return urllib.parse.urljoin(absolute, relative)

	def smart_str(self, s, encoding='utf-8', strings_only=False, errors='strict'):
		if strings_only and isinstance(s, (type(None), int)):
			return s
		if not isinstance(s, str):
			try:
				return str(s)
			except UnicodeEncodeError:
				return str(s).encode(encoding, errors)
		elif isinstance(s, str):
			return s.encode(encoding, errors)
		elif s and encoding != 'utf-8':
			return s.decode('utf-8', errors).encode(encoding, errors)
		else:
			return s
	
	def iri_to_uri(self, iri):
		if iri is None:
			return iri
		return urllib.parse.quote(self.smart_str(iri), safe='/#%[]=:;$&()+,!?*')
	
	
	@staticmethod
	def from_user_input(userInput):
		# Toma una URL en string y la transforma a un QUrl bien formado
		userInput = QString(userInput)
		
		trimmedString = userInput.trimmed()

		url = QUrl.fromEncoded(trimmedString.toUtf8(), QUrl.TolerantMode)
		urlPrepended = QUrl.fromEncoded((QLatin1String("http://") + trimmedString).toUtf8(), QUrl.TolerantMode)
	
		# Check the most common case of a valid url with scheme and host
		# We check if the port would be valid by adding the scheme to handle the case host:port
		# where the host would be interpretted as the scheme
		if (url.isValid()
			and not url.scheme().isEmpty()
			and (not url.host().isEmpty() or not url.path().isEmpty())
			and urlPrepended.port() == -1):
			return url
	
		# Else, try the prepended one and adjust the scheme from the host name
		if (urlPrepended.isValid() and (not urlPrepended.host().isEmpty() or not urlPrepended.path().isEmpty())):
			dotIndex = trimmedString.indexOf(".")
			hostscheme = trimmedString.left(dotIndex).toLower()
			if (hostscheme == QLatin1String("ftp")):
				urlPrepended.setScheme(QLatin1String("ftp"))
			return urlPrepended
	
		return QUrl() 
	