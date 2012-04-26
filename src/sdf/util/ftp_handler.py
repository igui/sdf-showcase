#! *- encoding: utf-8 -*
'''
Created on 14/01/2010

@author: AlejandroM
'''

import ftplib
import os.path

class FTPHandler(object):
    '''
    Clase que se encarga de la comunicación con un servidor FTP.
    Maneja inicio de conexiones y transferencia de archivos.
    '''


    def __init__(self, params=None):
        '''
        Constructor
        '''
        pass
    
    def upload_file(self, host_url, user_id, user_pass, file_name):
        '''
        Sube un archivo a un servidor FTP usando los datos de usuarios provistos.
        '''
        
        try:
            conn = ftplib.FTP(host_url)
        except Exception as ex:
            raise Exception('Host no accesible, revise el nombre del host o intentelo mas tarde. Error: ' + str(ex))            
        
        try:
            conn.login(user= user_id, passwd= user_pass)
        except Exception as ex:
            raise Exception('Nombre de usuario o clave incorrectos.')                            
        
        # Podemos usar cwd para cambiar el directorio en el servidor FTP.
        # conn.cwd('/var/www/html/incoming')
        
        f = file(file_name,'rb')
        try:
            conn.storbinary('STOR ' + os.path.basename(file_name), f)
            #print 'Archivo ' + file_name + ' fue subido correctamente.'
        except Exception as ex:
            raise Exception('Error al subir el archivo ' + file_name + ' al servidor ' + host_url + ': ' + str(ex))
        finally:
            conn.quit()
            f.close()
