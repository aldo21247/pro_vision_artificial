# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 10:52:05 2020

@author: anton
"""
class Persona:
    def __init__(self, id_persona, nombre, musica):
        self.id_persona = id_persona
        self.nombre = nombre
        self.musica = musica
    
    def __repr__(self):
        return self.nombre + ", " + str(self.musica)