import sqlite3
from .db_base import Basedatos
from ...resources.Tienda.Tienda import Tienda
import random


class Db_tiendas(Basedatos):
    """Permite interactuar con la talba tiedas"""

    def agregar_tienda(self, tienda):
        """Recibe un objeto de la clase Tienda y permite insertar sus datos en la 
        tabla tiendas."""

        if isinstance(tienda,Tienda):

            datos_tienda = [tienda.nombre_tienda, tienda.direccion_tienda,tienda.categoria,
             tienda.imagen_portada_tienda,tienda.correo_tienda,tienda.telefono_tienda,tienda.metadata_tienda]
            try:
                self.conectar_base_datos()
                self.cursor.execute('''INSERT INTO tiendas(
                                        nombre,direccion,categoria,
                                        ruta_imagen,correo,telefono,metadata) VALUES 
                                        (?,?,?,?,?,?,?);''', datos_tienda)
                self.commit()
                self.cursor.execute("SELECT id_tienda FROM tiendas ORDER BY id_tienda DESC LIMIT 1")
                id_t=self.cursor.fetchone()
                self.cerrar_conexion()
                return id_t[0]
            except sqlite3.IntegrityError :
                return False
        

    def modificar_datos_tienda(self, id_tienda, diccionario):
        """Modifica los datos almacenados en la base de datos, correspondientes 
        al id de la tienda, necesariamente se deben pasar los dos parametros 
        requeridos, id de la tienda, y el diccionario que se obtiene del formulario, con el nombre de la 
        columna y el dato nuevo."""

        for clave, valor in diccionario.items():
            nombre_columna=clave
            datos_nuevos=valor
        try:
            self.conectar_base_datos()
            self.cursor.execute("UPDATE tiendas SET {} = ? WHERE id_tienda = ?;"
								.format(nombre_columna), [datos_nuevos, id_tienda])
            self.commit()
            self.cerrar_conexion()
            return 
        except sqlite3.OperationalError:
            return False

    def devolver_lista_tiendas(self,tiendas,min=12):
        """Se utiliza internamente, toma una lista con los resultados de una consulta a
        la tabla tiendas y devuelve una lista de de diccionarios con los datos de cada tienda,
        si en la lista proporcionada no hubiera la cantidad de tiendas estipuladas en respuesta_minima(), 
        dicha funcion se encargara de completar la lista con "tiendas" por defecto"""

        lista_dict_tiendas=[]
        for registro in tiendas:
            dict_obj= {
                "id_tienda" : str(registro[0]),
                "nombre_tienda" : registro[1],
                "direccion_tienda" : registro[2],
                "categoria_tienda" : registro[3],
                "imagen_portada_tienda" : registro[4],
                "contacto" : registro[6],
                "correo_electronico" : registro[5],
                "meta_data" : registro[7]
            }
            lista_dict_tiendas.append(dict_obj)

        return (self.respuesta_minima(lista_dict_tiendas,min=min))
    
    def respuesta_por_defecto(self):
        """Genera un diccionario con datos por defecto para una tienda, cada vez que se ejecuta asigna al azar una
        ruta de imagen que corresponde con una imagen guardada en /static/img_tiendas/  """

        imagenes=["crear1","crear2","crear3","crear4"]
        ruta=random.choice(imagenes)
        return {
                    "id_tienda" : 'crear',
                    "nombre_tienda" : "Créa tu tienda",
                    "direccion_tienda" : "",
                    "categoria" : "",
                    "imagen_portada_tienda" : "/static/img_tiendas/"+ruta+".jpg",
                    "contacto" : "tutienda.com",
                    "correo_electronico" : "contacto@tutienda.com"
                }        

    
    def respuesta_minima (self,lista=[],min=12):
        """Puede recibir una lista, compruba que tenga la cantidad de elementos segun la variable 'min'(12), de ser
        necesario completa la lista con tiendas por defecto en formato.
        Si no se le pasa una lista en la llamada, crea una lista y la completa segun la variable 'min' con 
        tiendas por defecto en formato diccionario. Devuelve la lista completa.
         """
        while len(lista) < min:
            lista.append(self.respuesta_por_defecto())
        return(lista)

    def extraer_todas_tiendas(self):
        """Devuelve una lista de todas las tiendas almacenadas en la base 
        de datos, en formato diccionario"""

        self.conectar_base_datos()
        self.cursor.execute("SELECT * FROM tiendas")
        tiendas = self.cursor.fetchall()
        self.cerrar_conexion()
        
        if len(tiendas)==0:
            return self.respuesta_minima()
        else:
            return self.devolver_lista_tiendas(tiendas)

    def extraer_tienda(self, id_tienda=0,g=False,prueba=False, min=12): 
        """Extrae los datos de la tabla tiendas referentes al parámetro id.
        
        Retorna un diccionario generado a partir de los datos obtenidos, se puede almacenar en una variable 
        que se debe asignar en la declaración
        Ej: tienda_recuperada=Manager.extraer_tienda(id)
        Si la busqueda no obtiene resultados devuelve una Tienda por defecto 
		el parametro min indica la cantidad de tiendas que se devolveran 
        """
        if prueba:
            return[3,'nubre_prueba','direccion_prueba','telefono_prueba','datos varios']

        self.conectar_base_datos()
        self.cursor.execute("SELECT * FROM tiendas WHERE id_tienda = ?;", [id_tienda])
        tienda = self.cursor.fetchone()
        self.cerrar_conexion()
        if g:
            return tienda[0:6]#agregado 18-2-2020

        if str(tienda)== 'None': #verifica que la consulta devuelva algun dato
            return self.respuesta_minima(min=min) #objeto con datos por defecto
        else:
            return self.devolver_lista_tiendas([tienda],min=min)
    
    def extraer_n_tiendas_orden(self,n=10,orden='desc',contiene ='',columna=
                                'nombre||direccion||categoria||correo'):
        """Devuelve 10 ultimas tiendas, puede buscar coincidencia en columnas y variar el orden.
        Acepta parametros: n, orden, contiene y columna.El parametro n debe ser un
        numero entero representa la cantidad maxima de objetos a devolver, orden puede ser
        'desc' (descendente),'asc'(ascendente) o 'aleatorio'; 'contiene' representa
        el contenido que se desea buscar y 'columna' el nombre de la columna en la tabla.
        Devuelve una lista de Tiendas ordenada segun el parametro 'orden'. 
        """
        self.conectar_base_datos()
        if columna !='nombre' and columna != 'direccion' and columna !='categoria' and columna != 'correo':
            columna='nombre||direccion||categoria||correo' 
        
        if orden != 'desc' and orden != 'asc' and orden !='aleatorio':
            orden='desc'
        if orden == "aleatorio":
            self.cursor.execute("SELECT * FROM tiendas WHERE {} LIKE '%{}%' ORDER BY random() LIMIT ?;".format(columna,contiene),[n])
        else:
            self.cursor.execute("SELECT * FROM tiendas WHERE {} LIKE '%{}%' ORDER BY id_tienda {} LIMIT ?;".format(columna,contiene,orden),[n])     
        tiendas = self.cursor.fetchall()
        self.cerrar_conexion()
        if len(tiendas)==0:
            return self.respuesta_minima()
        else:
            return self.devolver_lista_tiendas(tiendas)
    def check(self,lista,contrasena):
        if contrasena == lista[1]:
            return (True,lista[0])
        else:
            return False

    def es_usuario(self,correo_tienda):
        self.conectar_base_datos()
        self.cursor.execute("SELECT id_tienda, metadata FROM tiendas WHERE correo = ?;", [correo_tienda])
        usuario=self.cursor.fetchone()
        self.cerrar_conexion()
        if usuario:
            return usuario
        return False
    def verificar_nombre_disponible(self,columna,nombre):
        #agregado 18-2-2020
        nombre=nombre.strip()
        columna=columna.strip()
        self.conectar_base_datos()
        try:
            self.cursor.execute("SELECT * FROM tiendas WHERE {} = ?".format(columna),[nombre])
            dato=self.cursor.fetchone()
            self.cerrar_conexion()
            if dato:
                return False
            return True
        except:
            print('error en verificar desde db')
            self.cerrar_conexion()
            return 'Error'

		
    def borrar_tienda(self, id_tienda):
        """Borra los datos almacenados en la base de datos, correspondientes al id de 
        la tienda, necesariamente se debe pasar el parámetro requerido id de la tienda
        a borrar, la funcion se encargara primero de borrar los productos relacionados con el id de la tienda."""

        try:
            self.conectar_base_datos()
            self.cursor.execute("DELETE FROM productos WHERE id_tienda_madre = ?;",[id_tienda])
            self.cursor.execute("DELETE FROM tiendas WHERE id_tienda = ?;", [id_tienda])
            self.commit()
            self.cerrar_conexion()
        except sqlite3.IntegrityError:
            return False
            
