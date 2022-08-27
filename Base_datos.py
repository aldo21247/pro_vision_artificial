# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 10:45:39 2020

@author: anton
"""
import sqlite3
from persona import Persona

"""
C: Create       INSERT  INSERT INTO nombre_tabla (parametros) VALUES (Valores)
R: Retrieve     SELECT  SELECT * from tabla;
U: Update       UPDATE  UPDATE tabla set 'valor_modificar' where 'clave_modificar'
D: Delete       DELETE  DELETE from tabla where valor=clave_elminar
"""

#Obtener conexión con la base de datos:
class Conexion:
    def create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect('database.db')
            print("Conexion exitosa a la base de datos ")
            
        except:
            print("Error")
            
        return connection
        
    #Crea la tabla con la que vamos a trabajar (3 atributos)
    def crear_tabla(self, conexion, cursor):
        try:
            sql = """
                DROP TABLE IF EXISTS Personas;
                CREATE TABLE Personas (
                id integer unique primary key autoincrement,
                name text,
                musica bool
                );
                """
            cursor.executescript(sql)
            print("se ha creado la tabla correctamente")
            
        except:
            print("Error al crear la tabla")
            conexion.rollback()
        
    #funcion para agregar usuarios        
    def insertar(self, conexion, cursor, nombre, musica):
        sql = "INSERT INTO Personas (name, musica) VALUES (?, ?);"
        # cursor.execute(sql)
        
        valores = (nombre, musica)
        try:
            cursor.execute(sql, valores)
            conexion.commit()
            print(nombre + "agregado a la base")
            
        except:
            print("Error al agregar usuario")
            conexion.rollback()      
        
    #Funcion para extraer datos de la tabla        
    def seleccionar(self, conexion, cursor):
        sql = "SELECT * from Personas"
        cursor.execute(sql)
        registros = cursor.fetchall()
        personas = []
        for registro in registros:
            persona = Persona(registro[0], registro[1], bool(registro[2]))        
            personas.append(persona)
                
        return personas
    
    def seleccionar_musica(self, conexion, cursor, atributo):
        sql = "SELECT * from Personas WHERE name = (?)"
        valores = (atributo,)
        cursor.execute(sql, valores)
        persona = cursor.fetchone()
        return persona[1], bool(persona[2])
        
    def actualizar(self, conexion, cursor, nombre_original, nuevo_nombre, musica):
        sql = "UPDATE Personas SET name = (?), musica = (?) WHERE name = (?)"
        valores = (nuevo_nombre, musica, nombre_original)
        try:
            cursor.execute(sql, valores)
            conexion.commit()
            print(nuevo_nombre + " actualizado en la lista")
        except:
            print("Error al actualizar usuario")
            conexion.rollback()
                
    def eliminar(self, conexion, cursor, nombre):
        sql = "DELETE from Personas WHERE name = (?)"
        valores = (nombre,)
        try:
            cursor.execute(sql, valores)
            conexion.commit()
            print(nombre + " ha sido eliminado de la lista")
        except:
            print("Error al eliminar usuario")
            conexion.rollback()

if __name__ == '__main__':
    conexion = Conexion().create_connection()
    cursor = conexion.cursor()
    Conexion().crear_tabla(conexion,cursor)
    Conexion().insertar(conexion, cursor, "Antonio", 0)
    nombre, estado = Conexion().seleccionar_musica(conexion, cursor, "Antonio")
    print(nombre, estado)
    Conexion().eliminar(conexion, cursor, "Antonio")
    cursor.close()
    conexion.close()
