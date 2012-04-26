# *- encoding: utf-8 -*
'''
Created on 14/09/2009

@author: iavas
'''
from sdf import SimpleParser
from sdf import Driver
from sdf.browsers.request import Request
from sdf.browsers.browserfactory import BrowserFactory
import http.client
from sdf.postactions.mail_sender import MailSender

class ASimpleParser(SimpleParser):
	def __init__(self, context):
		SimpleParser.__init__(self, context)
	
	def parse(self):
	
		mozilla_browser = BrowserFactory.get_instance().get_mozillabrowser()
		mozilla_browser.load_page("http://www.google.com.uy")
		
		print(mozilla_browser.get_html())
		
		print("DOONE!")

if __name__ == "__main__":
	args = "-p ASimpleParser -u ../../config/countries.info"	
	Driver().execute(args)
