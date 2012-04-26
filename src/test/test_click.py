'''
Created on 07/09/2009

@author: iavas
'''

from sdf import SimpleParser
from sdf import Driver
from os.path import join

class Parser(SimpleParser):
    def __init__(self, context):
        SimpleParser.__init__(self, context)
    
    def parse(self):
        browser = self.browser
        
        # carga el gallito 
        browser.load_page("http://localhost/testClick.html")
        elem = browser.find(tag = 'input')
        elem.click()
        
        elem = browser.find(tag = 'a')
        elem.click()
               
        print("DOONE!")
   

if __name__ == "__main__":
    args = [ "-p", "test.test_click.Parser",
             "-u", join('..', '..', 'config', 'countries.info'),
             "-W",
             "--wk-hide-images",
             "--wk-remain-open" ]    
    Driver().execute(args)