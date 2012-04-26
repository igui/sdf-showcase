# *- encoding: utf-8 -*
'''
Created on 20/08/2009

@author: iavas
'''
from sdf import SimpleParser
from sdf import Driver

class Parser(SimpleParser):
    def __init__(self, context):
        SimpleParser.__init__(self, context)
    
    def parse(self):
        browser = self.browser
        
        # carga google    
        browser.load_page("http://www.google.com")
        
        # pone don quijote en el campo de búsqueda 
        q = browser.find(name = 'q')
        print(q)
        q.set_value('don quijote')
        
		# hace click en el botón de buscar
        btng = browser.find(name = 'btnG')
        btng.click(wait_load_page = True)
        
        # agarra el primer link (que es a la wikipedia)
        link = browser.find(xpath = '// * [ @class="r"]/a[1]')
        print(link)
        link.click(wait_load_page = True)
        
        
        print("DOONE!")
   

if __name__ == "__main__":
    args = "-p Parser -W"     
    Driver().execute(args)