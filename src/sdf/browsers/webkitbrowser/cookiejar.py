'''
Created on 02/03/2010

@author: iavas
'''
from PyQt4.QtNetwork import QNetworkCookieJar


class CookieJar(QNetworkCookieJar):
	"""
	Una clase de cookieJar que almacena cookies pero
	permite decir si se usan o no
	"""


	def __init__(self, parent, accept_cookies):
		'''
		Inicia las cookies
		'''
		QNetworkCookieJar.__init__(self, parent)
		self.accept_cookies = accept_cookies
		
	
	def cookiesForUrl(self, url):
		"Da las cookies para una url dada"
		if self.accept_cookies:
			return QNetworkCookieJar.cookiesForUrl(self, url)
		else:
			return [] 
	
	def setCookiesFromUrl(self, cookie_list, url):
		if self.accept_cookies:
			return QNetworkCookieJar.setCookiesFromUrl(self, cookie_list, url)
		else:
			return False
