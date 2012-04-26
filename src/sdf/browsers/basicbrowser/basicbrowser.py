# *- encoding: utf-8 -*
import urllib.request, http.cookiejar
import lxml.html, lxml.etree
from sdf.exception import LoadPageError
from .. import browser
import chardet
from .domelement import DomElement
from sdf.util.typecheck import check_if_any_type, check_if_integral
import gzip
from sdf.browsers.proxy import ProxyListener
import re
from sdf.browsers.dom import DOM
from urllib.parse import urlparse
import http.client
from io import BytesIO
from sdf.browsers.request import Request
from urllib.error import HTTPError, URLError
import socket


#http.client.HTTPConnection.debuglevel = 1 

class BasicBrowser(browser.Browser, DOM):
	"""
	Un browser básico que se basa en hacer GET de páginas web
	
	.. image:: images/basicbrowser.png
	"""
	
	# cabezales de petición por defecto
	__default_headers =	{
		'User-Agent'		: 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0',
		'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language'	: 'es-es,es;q=0.8,en-us;q=0.5,en;q=0.3',
		'Accept-Encoding'	: 'gzip, deflate',		
		'Accept-Charset'	: 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
	}
	
	def __init__(self, context):
		"Crea un browser nuevo"
		browser.Browser.__init__(self, context)
		
		self.context = context
		self.__last_response = None
		
		self.__cookies = http.cookiejar.CookieJar()
		self.__opener = None
		self.__proxy = None
		proxy = self.context.proxies.get_current()
		self.set_proxy(proxy.host, proxy.port)
		
		self.context.proxies.add_change_listener(_Listener(self))
		
		# carga una página vacía
		#self._load_page(Request.get("about:blank"))
		
	def clear_cookies(self):
		"Limpia todas las cookies del browser" 
		self.__cookies = http.cookiejar.CookieJar()
		self.__reset_opener()
	
	def _download(self, url):
		http_request = urllib.request.Request(self.context.url_helper.iri_to_uri(url))
		return self.__opener.open(http_request).read()
	
	def _load_page(self, request):
		# setea los headers por defecto
		for header, default_value in self.__default_headers.items():
			if header not in request.headers:
				request.headers[header] = default_value
		
		url = self.context.url_helper.iri_to_uri(request.url)
		
		body = request.body
		if body is not None:
			body = body.encode('ascii')

		if request.method == 'GET':
			http_request = urllib.request.Request(url, None, request.headers)
		else:
			http_request = urllib.request.Request(url, body, request.headers)
	
		self.__last_response = None
		
		try:
			http_response = self.__opener.open(http_request)
		except HTTPError as ex:
			raise LoadPageError(
							"Error opening %s: %d, %s" % (url, ex.code, ex.msg),
							ex.code,
							ex.msg
							) 
			
		if http_response == None:
			raise ValueError("Critical error while trying to open url '%s'" % request.url)
		
		self.__last_response =  _Response(http_response, None, self.encoding)

		if self.__last_response.status != 200:
			raise LoadPageError("Cannot load page %s. Response code %d : %s" % 
								(request.url, self.__last_response.status,
								self.__last_response.reason))
		
		
	def get_elements_by_xpath(self, xpath):
		r = self.__last_response.dom.xpath(xpath)
		return [ DomElement(i, self) for i in r ]
	
	def get_url(self):
		return self.__last_response.url
	
	def get_html(self):
		return self.__last_response.source
	
	def get_page_encoding(self):
		return self.__last_response.encoding
	
	def __reset_opener(self):
		self.__opener = urllib.request.build_opener(
				_BasicBrowserHTTPHandler(),
				_BasicBrowserHTTPSHandler(),
				urllib.request.HTTPRedirectHandler(),
				urllib.request.HTTPDefaultErrorHandler(),
				urllib.request.HTTPCookieProcessor(self.__cookies),
				_AboutProtocolHandler(),
				urllib.request.ProxyHandler(self.__proxy),
		)
			
	def set_proxy(self, host = "", port = 80):
		"Pone el proxy HTTP en cierto host y puerto dado"

		check_if_any_type(host, str)
		check_if_any_type(port, [ str, int, int ])
		
		if isinstance(port, str):
			port = int(port)
				
		if not host:
			self.__proxy = {}
		else:		
			self.__proxy = {
						'http' : "%s:%d" % (host, port),
						'https' : "%s:%d" % (host, port)
						}
		
		
		self.__reset_opener()
		
	
class _Response(object):
	
	def __init__(self, http_response, error = None, encoding = 'auto'):
		"""
		Crea un objeto respuesta a partir de un http_response
		"""
		check_if_any_type(encoding, str)
		
		self.source = None
		self.dom = None
		self.reason = error
		self.status = 701
		self.headers = {}
		self.url = None
		self.encoding = None
		if not http_response:
			return
		
		self.status = http_response.code
		self.reason = http_response.msg
		self.headers = list(http_response.info().items())
		self.url = http_response.url
		if http_response.code != 200:
			return
		
		#rawdata = http_response.read()
		# FIX se usa un HTTPResponse patcheado: el texto está en el campo nuevo source
		rawdata = http_response.source
		
		
		# maneja la codificación en gzip
		if http_response.info()['content-encoding'] == 'gzip':
			rawdata = gzip.GzipFile(fileobj = BytesIO(rawdata)).read()

		if not rawdata:
			rawdata = b'<html><body></body></html>'
		
		if encoding == 'auto':
			# hay autodetección de caracteres
						
			# trata de buscar alguna declaración en el HTML o XML
			encoding_re = re.search(b'\<meta.*?charset=(.*?)\>', rawdata, re.I)
			if not encoding_re:
				encoding_re = re.search(b'\<\?xml.*encoding=(.*?)\?\>', rawdata, re.I)
			if encoding_re:
				encoding_str = encoding_re.group(1).decode('ascii', 'ignore')
				encoding = encoding_str.strip('" ')
				# busca la comilla si puede
				quote_idx = encoding.find('"')
				if quote_idx >= 0:
					encoding = encoding[:quote_idx]
			else:
				encoding = chardet.detect(rawdata)["encoding"]
				if encoding == None:
					raise LoadPageError("Couln't detect encoding for page")
		
		self.encoding = encoding
				
		# Elimino la declaración de encoding
		rawdata = re.sub(b'\<\?xml.*encoding=(.*?)\?\>', '',rawdata, re.I)
		self.source = rawdata.decode(encoding, "ignore")
		if len(self.source.strip()) > 0:
			parser = lxml.html.HTMLParser()
			try:
				self.dom = lxml.etree.HTML(self.source, parser)
			# se da si el documento ya define el encoding explícitamente
			except ValueError: 
				import traceback;traceback.print_exc()
				self.source = self.source.encode( "utf-8" )
				self.dom = lxml.etree.HTML(self.source, parser)
			
			self.dom.make_links_absolute(self.url, False)
	
	def is_ok(self):
		return self.status == 200 

class _Listener(ProxyListener):
	"Escucha para cambiar el proxy"
	def __init__(self, browser):
		ProxyListener.__init__(self)
		self.__browser = browser
		
	def on_proxy_change(self, proxy):
		self.__browser.set_proxy(proxy.host, proxy.port)

class _AboutProtocolHandler(urllib.request.BaseHandler):
	"""
	Se encarga de manejar el protocolo about:
	"""
	
	__default_about_blank = b"""
	<html>
		<head>
		<title>about:blank</title>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
		</head>
		<body></body>
	</html>
	"""
	
	def __init__(self):
		pass
	
	def about_open(self, req):
		url = req.get_full_url()
		path = urlparse(url)[2] 
		if path != 'blank': # solo soporta about:blank
			return _AboutProtocolResponse(
										"",
										url,
										http.client.NOT_FOUND,
										http.client.responses[http.client.NOT_FOUND],
										{}
										)
		else:
			return _AboutProtocolResponse(
										self.__default_about_blank,
										url,
										http.client.OK,
										http.client.responses[http.client.OK],
										{}
										)  
		
class _AboutProtocolResponse(urllib.request.addinfourl):
	def __init__(self, buf, url, code, msg, headers):
		check_if_any_type(buf, bytes)
		check_if_any_type(url, str)
		check_if_integral(code)
		check_if_any_type(msg, str)
		check_if_any_type(headers, dict)
				
		urllib.request.addinfourl.__init__(
								self,
								BytesIO(buf),
								_AboutProtocolHeader(headers),
								url,
								code
								)

		self.msg = msg
		
class _AboutProtocolHeader():
	def __init__(self, headers):
		check_if_any_type(headers, dict)
		self.__headers = headers
	
	def __getitem__(self, h):
		return self.__headers.get(h, None)
		
	def getheader(self, h, v):
		return self.__headers.get(h, v)
	
	def getheaders(self):
		return list(self.__headers.items())
	
	def items(self):
		return list(self.__headers.items())


class _PrereadHTTPHandler(object):
	"""
	Clase que es parecida al AbstractHTTPHandler pero deja la respuesta del
	HTTPResponse en un campo especial source
	"""
	
	@classmethod
	def do_open(cls, http_class, req, **http_conn_args):
		"""Return an HTTPResponse object for the request, using http_class.

		http_class must implement the HTTPConnection API from http.client.
		"""
		host = req.host
		if not host:
			raise URLError('no host given')

		# will parse host:port
		h = http_class(host, timeout=req.timeout, **http_conn_args)

		headers = dict(req.unredirected_hdrs)
		headers.update(dict((k, v) for k, v in req.headers.items()
							if k not in headers))

		headers["Connection"] = "close"
		headers = dict((name.title(), val) for name, val in headers.items())

		if req._tunnel_host:
			tunnel_headers = {}
			proxy_auth_hdr = "Proxy-Authorization"
			if proxy_auth_hdr in headers:
				tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
				# Proxy-Authorization should not be sent to origin
				# server.
				del headers[proxy_auth_hdr]
			h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

		try:
			h.request(req.get_method(), req.selector, req.data, headers)
			r = h.getresponse()  # an HTTPResponse instance
			
			#### FIX: siempre lee antes y lo pone en el campo source
			r.source = r.read()
			
		except socket.error as err:
			raise URLError(err)
		finally:
			h.close()

		r.url = req.get_full_url()
		r.msg = r.reason
		return r


class _BasicBrowserHTTPHandler(urllib.request.HTTPHandler):
	"""
	Clase de fix para un bug feo de python con la librería urllib.request
	"""
	
	def do_open(self, http_class, req, **http_conn_args):
		return _PrereadHTTPHandler.do_open(http_class, req, **http_conn_args)
	
	def __init__(self, debuglevel = 0):
		urllib.request.HTTPHandler.__init__(self, debuglevel)


class _BasicBrowserHTTPSHandler(urllib.request.HTTPSHandler):
	"""
	Clase de fix para un bug feo de python con la librería urllib.request
	"""
	
	def do_open(self, http_class, req, **http_conn_args):
		return _PrereadHTTPHandler.do_open(http_class, req, **http_conn_args)

	def __init__(self, debuglevel=0, context=None, check_hostname=None):
		urllib.request.HTTPSHandler.__init__(self, debuglevel)


