import sqlite3
import random
from .db_base import Basedatos
from ...resources.Producto.Producto import Producto

class Db_productos(Basedatos):
    """Permite interactuar con la tabla productos."""
    
    def agregar_producto(self, producto,id_tienda_madre):
        """Recibe objeto Producto a guardar y el id de la  Tienda al que esta relacionado.
        
        Asigna automaticamente un id unico a cada producto y lo relaciona con el id su tienda,
        No se insertaran productos cuando exista otro registro con el cual coincida exactamente
        la combinacion de los datos de 'nombre', 'descripcion','ruta_imagen'
        e 'id_tienda_madre' """
        if isinstance(producto, Producto):

            datos_producto = [id_tienda_madre,
                              producto.nombre_producto,
                              producto.descripcion_producto,
                              producto.imagen_producto,
                              producto.precio_producto,
                              producto.metadata_producto
                              ]
            try:
                self.conectar_base_datos()
                self.cursor.execute('''INSERT INTO productos(
                                        id_tienda_madre,nombre,descripcion,
                                        ruta_imagen,precio,metadata) VALUES 
                                        (?,?,?,?,?,?);''', datos_producto)
                self.commit()
                self.cerrar_conexion()
                
            except sqlite3.IntegrityError:
                return False
    def modificar_datos_producto(self,id_producto,diccionario):

        for clave,valor in diccionario.items():
            nombre_columna = clave
            datos_nuevos = valor
        try:

            self.conectar_base_datos()
            self.cursor.execute("UPDATE productos SET {} = ? WHERE id_producto = ?;"
                                .format(nombre_columna), [datos_nuevos, id_producto])

            self.commit()
            self.cerrar_conexion()
        except sqlite3.OperationalError:
            return False
        
    def producto_por_defecto(self):
        imagenes=["producto1","producto2","producto3"]
        ruta=random.choice(imagenes)

        return {    "id_producto" : "crear",
                    "imagen_producto" : "/static/img_productos/"+ruta+".jpg",
                    "nombre_producto" : "Crea tu tienda",
                    "precio_producto" : "",
                    "descripcion_producto" : "",
                   
                }
    
    def respuesta_minima_producto (self,lista=[]):
        min=1
        while len(lista) < min:
                lista.append(self.producto_por_defecto())
        return(lista)
        
    def devolver_lista_productos(self,producto):
        """ Se utiliza internamente, toma una lista con los resultados de una 
        consulta a la tabla productos, devuelve una lista de objetos Producto"""

        lista_dict_productos=[]
        for registro in producto:
            dict_obj= {
                "id_producto" : registro[0],
                "nombre_producto" : registro[1],
                "descripcion_producto" : registro[2],
                "imagen_producto" : registro[3],
                "precio_producto" : registro[4],
                "metadata_producto" : registro[5],
                "id_tienda_madre" : registro[6],
            }
            lista_dict_productos.append(dict_obj)

        return (lista_dict_productos)

    def extraer_productos_tienda(self,id_tienda=''): 
        """Recibe un id de Tienda, retorna lista de todos los objetos Producto relacionados 
        a ella. Si no se le especifica el parametro devuelve 20 productos al azar"""

        if id_tienda=="":
            id_tienda='ORDER BY random() LIMIT 20'
        else:
            id_tienda='WHERE id_tienda_madre ={} '.format(id_tienda)
            
            
        
        self.conectar_base_datos()
        self.cursor.execute( " SELECT * FROM productos {};".format(id_tienda))
        
        productos = self.cursor.fetchall()
        self.cerrar_conexion()
        if len(productos)==0:
            return self.respuesta_minima_producto()
        else:
            return self.devolver_lista_productos(productos)


    def extraer_productos_coinciden(self,n=10,contiene ='',columna=
                                'nombre||descripcion||precio',orden='desc'):
        """Devuelve 10 ultimos productos, puede buscar coincidencia en columnas y 
        variar el orden.

        Acepta parametros: n, orden, contiene y columna. El parametro n debe ser un
        numero entero representa la cantidad maxima de objetos a devolver, orden puede ser
        'desc' (descendente),'asc'(ascendente) o 'aleatorio'; 'contiene' representa
        el contenido que se desea buscar y 'columna' el nombre de la columna en la tabla.
        Devuelve una lista de Productos ordenada segun el parametro 'orden'.
        """

        if columna != 'nombre' and columna != 'descripcion' and columna != 'precio':
            columna = 'nombre||descripcion||precio'

        self.conectar_base_datos()
        if orden != 'desc' and orden != 'asc' and orden !='aleatorio':
            orden='desc'
        if orden == "aleatorio":
            self.cursor.execute("SELECT * FROM productos WHERE {} LIKE '%{}%' ORDER BY random() LIMIT ?;".format(columna,contiene),[n])
        else:
            self.cursor.execute("SELECT * FROM productos WHERE {} LIKE '%{}%' ORDER BY id_producto {} LIMIT ?;".format(columna,contiene,orden),[n])
            
        productos = self.cursor.fetchall()
        self.cerrar_conexion()
        if len(productos) == 0:
            return self.respuesta_minima_producto()
        else:
            return self.respuesta_minima_producto(self.devolver_lista_productos(productos))
    def extraer_producto_id_tienda_id_producto (self,id_tienda,id_producto):
        self.conectar_base_datos()
        self.cursor.execute("SELECT * FROM productos WHERE id_tienda_madre = ? AND id_producto = ?;",[id_tienda, id_producto])
        producto = self.cursor.fetchall()
        return self.devolver_lista_productos(producto)

    def borrar_producto(self, id_producto, id_tienda):

        """Recibe id_producto e id_tienda y borra el producto"""
        try:
            self.conectar_base_datos()
            self.cursor.execute("DELETE FROM productos WHERE id_producto = ? AND id_tienda_madre = ?;", [id_producto, id_tienda])
            self.commit()
        except sqlite3.OperationalError:
            return False
 

