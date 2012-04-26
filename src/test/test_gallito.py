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
        browser.load_page("http://www.gallito.com/trabajo.aspx")
        
        html = browser.find(tag = 'html')
        print(html.extract("'#'"))
        
        
        elem = browser.find(tag = 'select', class_name = "Arial11_55585B" )
        print(elem)
       
        child = elem.find(tag = 'option')
        print(child)
        child.click()
       
        print("fuck!")
   

if __name__ == "__main__":
    args = [ "-p", "test.test_gallito.Parser",
             "-u", join('..', '..', 'config', 'countries.info'),
             "-W",
             "-M 5",
             "--wk-hide-images",
             "--wk-remain-open" ]    
    Driver().execute(args)
