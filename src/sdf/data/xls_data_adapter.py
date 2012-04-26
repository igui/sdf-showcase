# *- encoding: utf-8 -*
'''
Created on 06/08/2010

@author: AlejandroM
'''

try:
    import xlwt
except ImportError:
    raise ImportError(r'No se pudo encontrar el modulo xlwt. Se puede obtener en: http://pypi.python.org/pypi/xlwt')

from sdf.data_adapter import DataAdapter

class XlsDataAdapter(DataAdapter):
    '''
    Clase base para crear data adapters que escriban en formato XLS (hojas de cálculo).
    Hereda de la clase básica de data adapters: DataAdapter.
    '''
    
    def __init__(self, context=None, header=[], outfile_name='salida.xls', sheet_name='hoja', start_row=0):
        '''
        Construye un objeto XlsDataAdapter con los parametros necesarios.        
        '''
        # Cantidad máxima de filas en un archivo XLS válido.
        self.__MAX_ROWS = 65000
        # Cabezal del archivo de datos. Es lo que se escribe en la fila cero de cada hoja.
        self.header = header
        # Nombre que tendrán las hojas de datos.
        self.sheet_name = sheet_name
        # Formato por defecto para las filas cabezal
        self.header_format = xlwt.easyxf('align: horz center; font: bold on')
        # Nombre del archivo de salida. Debe abrirse en modo 'wb', no 'w'.
        if context is not None:
            self.outfile_name = context.options.output_file
        else:
            self.outfile_name = outfile_name
        
        self.__start_row = start_row

        # TODO: Hacerlo mas "INSTANCIABLE". Escrituras solo se hacen en sub clases!

    def set_header(self, header):
        self.header = header
    
    def set_header_format(self, str_format):
        'Recibe un string con formato easyfx y con el crea un estilo para lo cabezales.'
        try:
            format = xlwt.easyxf(str_format)
            self.header_format = format
        except:
            # TODO: Lanzar una excepción?
            print('[ERROR] Formato de celda invalido: ' + str_format)
    
    def append_header(self, sheet):
        '''
        Dada una hoja agrega en la primer fila un elemento de cabezal por columna.
        Ej:
            cabezal = ['nombre', 'ciudad', 'pais']    ==>
                A         B        C
            0 nombre    ciudad    pais
            1
            2
        '''
        for i in range(len(self.header)):
            # Especifico el ancho de la columna. Con este numero se ve realtivamente bien.
            sheet.col(i).width = (len(self.header[i]) * 0x0d00) / 5
            sheet.write(self.__start_row, i, self.header[i], self.header_format)


    def write_items(self, items):

        # TODO: Aca hay que guardar ela rchivo y eso? Se maneja aca o en la subclase??

        # Creo el libro
        book = xlwt.Workbook()
        sheet = book.add_sheet(self.sheet_name)
        self.append_header(sheet)

        row = self.__start_row + 1; total = 0; sheet_count = 1    
        for item in items:
            self.write_item(item, sheet, row)
            row += 1
            total += 1
            if row == self.__MAX_ROWS:
                print('[DEBUG] Se lleno la pagina '+ str(sheet_count) +' con ' + str(self.__MAX_ROWS) + ' items.')
                sheet_count += 1
                sheet = book.add_sheet('%s(%s)' % (self.sheet_name, str(sheet_count),))
                self.append_header(sheet)
                row = self.__start_row + 1            
        print('[DEBUG] Hecho. Procesados', total, 'items en', sheet_count,'paginas.')
        
        # Guardar el libro en un archivo.
        with open(self.outfile_name, 'wb') as f:
            book.save(f)
        print('[INFO] Escritura completada (%s items).' % (total))
        
    def write_string_data(self, data, sheet, row, column):
        sheet.write(row, column, data)
        
    def write_list_data(self, data, sheet, row, column, sep=', '):
        sheet.write(row, column, sep.join(data))
    
    def get_column_number(self, name):
        return self.header.index(name)
    
    def write_item(self, item, sheet, row):
        raise NotImplementedError('Es necesario implementar la funcion write_item() en el Data Adapter.')
        
        # Metodo Abstracto --- Esto es un ejemplo
        
        # El objeto Item tiene los atributos id, titulo y nombre.
        # El header se definio como: ['Id', 'Titulo', 'Nombre']
        col_actual = self.get_column_number('Id')
        self.write_string_data(item.id, sheet, row, col_actual)        
        col_actual = self.get_column_number('Titulo')
        self.write_string_data(item.titulo, sheet, row, col_actual)
        col_actual = self.get_column_number('Nombre')
        self.write_string_data(item.nombre, sheet, row, col_actual)        
        

# -- Ejemplos de formato --
    # style_header = xlwt.easyxf('align: horz center; font: bold on', num_format_str='#,##0.00')
    # hoja.write(2, 2, xlwt.Formula("A3+B3"))
    