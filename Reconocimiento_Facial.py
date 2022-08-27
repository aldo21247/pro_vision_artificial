 # -*- coding: utf-8 -*-
"""

"""
from persona import Persona
from Base_datos import Conexion
import cv2 as cv
import os
from os import listdir
from os.path import isfile, join
import sys
from time import sleep
import numpy as np
from tkinter import *
import tkinter.font as tkFont
from Detectar_celulares import detectar_celulares

clasificador_rostros = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
if clasificador_rostros.empty():
    raise IOError('No se ha encontrado el clasificador de rostros')

class reconocimiento_facial():
    #=Retorna la conexion a la base de datos, y un cursor para realizar acciones=
    def inicializar_DB(self):
        conexion = Conexion().create_connection()
        cursor = conexion.cursor()
        return conexion, cursor
    
    #==============Crea la tabla personas, solo se ejecutará una vez==========
    def tabla(self, conexion, cursor):
        Conexion().crear_tabla(conexion, cursor)
    
    #=======================Termina la conexión con la base de datos==========
    def cerrar_DB(self, conexion, cursor):
        cursor.close()
        conexion.close()
        
    #========================FUNCION DETECTAR-RECORTAR ROSTROS================
    def detector_rostros(self, imagen):
        gray = cv.cvtColor(imagen, cv.COLOR_BGR2GRAY)
        rostro = clasificador_rostros.detectMultiScale(gray, 1.3, 3)
        
        if rostro == ():
            return None
        
        for (x,y,w,h) in rostro:
            imagen_recortada = imagen[y:y+h, x:x+w]
    
        return imagen_recortada
    
    #==============FUNCIÓN PARA OBTENER FOTOGRAFIAS DEL USUARIO===============
    def obtener_fotografias(self, nombre_carpeta): 
    
        capture = cv.VideoCapture(0)
        contador_rostros = 0          
        while True:
            ret, frame = capture.read()
            
            if not ret:
                break
            
            if self.detector_rostros(frame) is not None:
                contador_rostros += 1
                resized_frame = cv.resize(self.detector_rostros(frame), (250, 250))
                gray = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
                path = './'+ nombre_carpeta +'/' + str(contador_rostros) + '.jpg'
                cv.imwrite(path, gray)
                cv.putText(gray, str(contador_rostros), (50, 50), cv.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                cv.imshow('Cropped', gray)
                  
            else:
                print("rostro no detectado")
                pass
            
            if cv.waitKey(1) == 27 or contador_rostros == 30: 
                break
        
        
        capture.release()
        cv.destroyAllWindows()
        
    #====================FUNCIÓN PARA COMPROBAR SI YA EXISTE EL USUARIO=======    
    def comprobar(self, nombre_carpeta, conexion, cursor):
        if os.path.exists(nombre_carpeta):
            return True 
        else:
            return False
            
    #====================FUNCIÓN PARA CREAR NUEVO USUARIO=====================
    def crear(self, nombre_carpeta):
        if not os.path.exists(nombre_carpeta):
            os.makedirs(nombre_carpeta)
            
    #============FUNCIÓN PARA ENTRENAR Y CREAR ARCHIVO DE RECONOCIMIENTO======
    def entrenar(self, nombre_carpeta, n_usuario):
        direccion = './' + nombre_carpeta + '/'
        
        direccion_archivos = [i for i in listdir(direccion) if isfile(join(direccion, i))]
    
        entrenamiento, etiquetas = [], []
        
        for i, archivos in enumerate(direccion_archivos):
            direccion_imagen = direccion + direccion_archivos[i]
            imagenes_entrenamiento = cv.imread(direccion_imagen, cv.IMREAD_GRAYSCALE)
            entrenamiento.append(np.array(imagenes_entrenamiento, np.uint8))
            etiquetas.append(i)
        
        entrenamiento = np.array(entrenamiento)
        etiquetas = np.array(etiquetas)    
        reconocedor_rostros = cv.face.LBPHFaceRecognizer_create()
        reconocedor_rostros.train(entrenamiento, etiquetas)
        reconocedor_rostros.save('trainingData'+str(n_usuario)+'.yml')
        print("Entrenamento exitoso.")
    
    #====================FUNCIÓN DE RECONOCIMIENTO FACIAL=====================    
    def reconocimiento(self, conexion, cursor):
        path = os.getcwd()
        direcciones = [i for i in listdir(path) if i.endswith('yml')]
        i = 0
        contador_exitos = 0
        contador_fracasos = 0
        
        if direcciones is []:
            print("El algoritmo aún no ha sido entrenado.")
            sys.exit()
        
        face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        cap = cv.VideoCapture(0)
            
        while True:
            while i < len(direcciones):
                reconocedor = cv.face.LBPHFaceRecognizer_create()
                archivo = direcciones[i]
                reconocedor.read(archivo)
                ret, frame = cap.read()
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                
                try:
                    rostros = face_cascade.detectMultiScale(gray, 1.3, 3
                    )
                    for (x,y,w,h) in rostros:
                        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 3)
                        ids,conf = reconocedor.predict(gray[y:y+h,x:x+w])
                        result = Conexion().seleccionar(conexion, cursor)
                        nombre = result[i].nombre
                            
                        if conf < 50:
                            contador_exitos += 1
                            #print(contador_exitos)
                            cv.putText(frame, nombre, (x+2,y+h-5), cv.FONT_HERSHEY_SIMPLEX, 1, (150,255,0),2)
                            if contador_fracasos > 30:
                                contador_exitos = 0
                            if contador_exitos > 10:
                                cap.release()
                                cv.destroyAllWindows()
                                return nombre
                                
                        else:
                            contador_fracasos+=1
                            print(contador_fracasos)
                            cv.putText(frame, 'No reconocido.', (x+2,y+h-5), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                            if contador_fracasos > 20:
                                contador_fracasos = 0
                                i+=1 
                                if i >= len(direcciones):
                                    cap.release()
                                    cv.destroyAllWindows()
                                    return None
                                
                except:
                    print("contador_fracasos")
                    
                cv.imshow('Reconocimiento Facial',frame)
                k = cv.waitKey(1)
                if (k == 27):
                    break
                
    #=====================FUNCIÓN PARA EJECUTAR LA PRIMERA VEZ================
    def primera_ejecucion(self, conexion, cursor):
        root = Tk()
        root.title(" Sistema de vision artificial para el monitoreo de conductas e indicadores de animo")
        root.resizable(0,0)
        root.geometry('800x420')
        root.config(cursor="pirate",bg="silver",bd=15,relief="ridge")
        menubar = Menu(root)
        

        # Variables
        Contraseña = StringVar()
        Contraseña2 = StringVar()
        Nombre1 = StringVar()
        helv36 = tkFont.Font(family='Arial', size=9, weight="bold")
        Imagen1 = PhotoImage(file="robot.gif")
        Imagen2 = PhotoImage(file="si.png")
        Imagen3 = PhotoImage(file="no.png")
        Imagen4 = PhotoImage(file="rf1.png")
        
        
        #///////////////////////////////////////////FUNCIONES////////////////////////////////////////////////
        def primera_pagina():

            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root, text="¡Bienvenido!\n ¿Usted es el dueño del auto?")
            label.place(x=100, y=10)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 24, "bold"))
            b1 = Button(root, relief="ridge", overrelief="flat", command=si1, width=80, height=80,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(x=260,
                                                                                                               y=140)
            b2 = Button(root, relief="ridge", overrelief="flat", command=no1, width=80, height=80,
                        anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400, y=140)

        def si1():

            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root, text="¡Es un placer! \n crearemos su cuenta de super usuario\n ¿Cual es su nombre?")
            label.place(x=30, y=10)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 24, "bold"))
            Entry(root, width=20, fg="black", textvariable=Nombre1, bd=18, justify="center").place(x=276, y=180)
            b3 = Button(root, text="listo", relief="ridge", overrelief="flat", command=listo1, width=10, height=2,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36, fg="black").place(x=490,
                                                                                                             y=180)
            Volver = Button(root, text="volver", relief="ridge", overrelief="flat", command=primera_pagina, width=10,
                            height=1,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=320)

        def no1():

            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                          text="Esperaremos al dueño del auto \npara crear al super usuario\n\n¡Hasta la proxima!")
            label.place(x=20, y=10)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 30, "bold"))

            Volver = Button(root, text="volver", relief="ridge", overrelief="flat", command=primera_pagina, width=10,
                            height=1,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=600, y=320)

        def listo1():
            nombre = Nombre1.get()
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root, text="Digite su pasword  " + nombre)
            label.place(x=220, y=10)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))
            entry = Entry(root, width=20, textvariable=Contraseña, show="*", bd=18, justify="center")
            entry.place(x=276, y=60)

            label = Label(root, text="Confirme su pasword")
            label.place(x=220, y=120)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))
            entry = Entry(root, width=20, show="*", textvariable=Contraseña2, bd=18, justify="center")
            entry.place(x=276, y=180)

            b7 = Button(root, text="listo", relief="ridge", overrelief="flat", command=listo2, width=10, height=2,
                        anchor="center",
                        bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=500, y=180)

        def listo2():
            password = Contraseña.get()
            password2 = Contraseña2.get()
            if password2 == password:
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root,
                              text="¿Desea activar el sistema de reproduccion musical \n basada en su estado de animo?")
                label.place(x=10, y=20)
                label.config(fg="blue",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 19, "bold"))
                b4 = Button(root, relief="ridge", overrelief="flat", command=si2, width=80, height=80,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(
                    x=260, y=140)
                b5 = Button(root, relief="ridge", overrelief="flat", command=no2, width=80, height=80,
                            anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400,y=140)
            else:
                label = Label(root,
                              text=" ¡ NO COINCIDEN LAS CONTRASEÑAS! ")
                label.place(x=380, y=280)
                label.config(fg="blue",  # Foreground
                             bg="gold",  # Background
                             font=("Ebrima", 13, "bold"))

        def si2():
            nombre = Nombre1.get()
            musica = 1
            self.tabla(conexion, cursor)
            Conexion().insertar(conexion, cursor, nombre, musica)
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                          text="Coloquese frente a la camara para registrarlo \n\n la camara se activara en 10 segundos \ndespues de que presione 'listo' ")
            label.place(x=13, y=5)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 21, "bold"))
            b5 = Button(root, text="listo", font=helv36, relief="ridge", overrelief="flat", command=acabamos, width=15,
                        height=5,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=590, y=280)

        def no2():
            nombre = Nombre1.get()
            musica = 0
            self.tabla(conexion, cursor) 
            Conexion().insertar(conexion, cursor, nombre, musica)
        
            

            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                          text="Coloquese frente a la camara para registrarlo \n\n la camara se activara en 10 segundos \ndespues de que presione 'listo' ")
            label.place(x=13, y=5)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 21, "bold"))
            b5 = Button(root, text="listo", font=helv36, relief="ridge", overrelief="flat", command=acabamos, width=15,
                        height=5,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=590, y=280)

        def acabamos():
            sleep(10)

            n_usuario=0
            nombre = Nombre1.get()
            password = Contraseña.get()
            nombre_carpeta = nombre.lower()
            SU = [nombre + "\n", password]
            if not os.path.exists(nombre_carpeta):
                os.makedirs(nombre_carpeta)
            capture = cv.VideoCapture(0)
            contador_rostros = 0          
            while True:
                ret, frame = capture.read()
                
                if not ret:
                    break
                
                if self.detector_rostros(frame) is not None:
                    contador_rostros += 1
                    resized_frame = cv.resize(self.detector_rostros(frame), (250, 250))
                    gray = cv.cvtColor(resized_frame, cv.COLOR_BGR2GRAY)
                    path = './'+ nombre_carpeta +'/' + str(contador_rostros) + '.jpg'
                    cv.imwrite(path, gray)
                    cv.putText(gray, str(contador_rostros), (50, 50), cv.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                    cv.imshow('Cropped', gray)
                      
                else:
                    
                    pass
                
                if cv.waitKey(1) == 27 or contador_rostros == 30: 
                    break
            
            
            capture.release()
            cv.destroyAllWindows()
            direccion = './' + nombre_carpeta + '/'
        
            direccion_archivos = [i for i in listdir(direccion) if isfile(join(direccion, i))]
        
            entrenamiento, etiquetas = [], []
            
            for i, archivos in enumerate(direccion_archivos):
                direccion_imagen = direccion + direccion_archivos[i]
                imagenes_entrenamiento = cv.imread(direccion_imagen, cv.IMREAD_GRAYSCALE)
                entrenamiento.append(np.array(imagenes_entrenamiento, np.uint8))
                etiquetas.append(i)
            
            entrenamiento = np.array(entrenamiento)
            etiquetas = np.array(etiquetas)    
            reconocedor_rostros = cv.face.LBPHFaceRecognizer_create()
            reconocedor_rostros.train(entrenamiento, etiquetas)
            reconocedor_rostros.save('trainingData'+str(n_usuario)+'.yml')
            
            list = root.place_slaves()
            for l in list:
                l.destroy()
            list2 = root.pack_slaves()
            for l in list2:
                l.destroy()    
            label = Label(root,
                          text="Terminamos \n ¡Buen viaje!")
            label.place(x=280, y=30)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 24, "bold"))
            Label(root, image=Imagen4, bd=5).place(x=300, y=180)
            cerrar = Button(root, text="cerrar", relief="ridge", overrelief="flat", command=close_window, width=10,
                            height=1,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=320)



            with open("SU.txt", "w") as f:

                f.writelines(SU)

        def close_window():
            root.destroy()
        def lista_usr():
            list2 = root.place_slaves()
            for l in list2:
                l.destroy()
            label = Label(root, text="True significa que la musica basada en el animo está activada\nFalse que está desactivada.\nLos usuarios registrados en la base de datos son:")
            label.config(fg="black",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 15, "bold"))
            label.place(x=10, y=20)
            personas = Conexion().seleccionar(conexion, cursor)
            contador=100
            for p in personas:
                contador+=29
                label = Label(root, text=p)
                label.config(fg="green",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 15, "bold"))
                label.place(x=160, y=contador)
        #////////////////////////////////////MAIN////////////////////////     
        Label(root, image=Imagen1, bd=5).pack(side="bottom")
        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label="Usuarios registrados",command=lista_usr)
        filemenu.add_command(label="Modificar Usuarios",command=quit)
        
        menubar.add_cascade(label="Opciones", menu=filemenu)
        menubar.add_command(label="Acerca del sistema", command=quit)
        menubar.add_command(label="Ayuda",command=close_window)
        root.config(menu=menubar)
        primera_pagina()
        root.mainloop()
        
        nombre=Nombre1.get()
        nombre, validar_musica = Conexion().seleccionar_musica(conexion, cursor, nombre)
        return nombre, validar_musica
        
     
    #==================FUNCIÓN PARA EJECUTAR CADA QUE SE INICIE===============  
    def reconocer(self, conexion, cursor, password):
        
        personas = Conexion().seleccionar(conexion, cursor) 
        n_usuario = (len(personas))
        nombre = self.reconocimiento(conexion, cursor)
        root =Tk()
        root.title(" Sistema de vision artificial para el monitoreo de conductas e indicadores de animo")
        root.resizable(0,0)
        root.geometry('800x420')
        root.config(cursor="pirate",bg="silver",bd=15,relief="ridge")
        menubar = Menu(root)
        

        # Variables
        filemenu = Menu(menubar, tearoff=0)
        Contraseña = StringVar()
        Nombre1 = StringVar()
        helv36 = tkFont.Font(family='Arial', size=9, weight="bold")
        Imagen1 = PhotoImage(file="robot.gif")
        Imagen2 = PhotoImage(file="si.png")
        Imagen3 = PhotoImage(file="no.png")
        Imagen4 = PhotoImage(file="rf1.png")
        def lista_usr():
            list2 = root.place_slaves()
            for l in list2:
                l.destroy()
            label = Label(root, text="True significa que la musica basada en el animo está activada\nFalse que está desactivada.\nLos usuarios registrados en la base de datos son:")
            label.config(fg="black",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 15, "bold"))
            label.place(x=10, y=20)
            personas = Conexion().seleccionar(conexion, cursor)
            contador=100
            for p in personas:
                contador+=29
                label = Label(root, text=p)
                label.config(fg="green",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 15, "bold"))
                label.place(x=160, y=contador)
        def seleccionar_nombres(conexion, cursor):
            sql = "SELECT name from Personas"
            cursor.execute(sql)
            registros = cursor.fetchall()
            nombres = []
            for registro in registros:
                nombres.append(registro[0])        
                    
            return nombres        
        def actualizar_usuario():
            list2 = root.place_slaves()
            for l in list2:
                l.destroy()
            label = Label(root, text="Digite el password del superusuario")
            label.place(x=140, y=80)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))
            entry = Entry(root, width=20, textvariable=Contraseña, show="*", bd=18, justify="center")
            entry.place(x=276, y=180)
            b7 = Button(root, text="listo", relief="ridge", overrelief="flat", command=hecho, width=10, height=2,
                        anchor="center",
                        bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=500, y=180)
               
        def hecho():
            password2 = Contraseña.get()
            
            
            if password2 == password:
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root, text="¿Cual es el nombre del usuario que desea actualizar?")
                label.place(x=5, y=100)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 18, "bold"))
                Entry(root, width=20, fg="black", textvariable=Nombre1, bd=18, justify="center").place(x=276, y=180)
                b3 = Button(root, text="listo", relief="ridge", overrelief="flat", command=hecho2, width=10, height=2,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36, fg="black").place(x=490,
                                                                                                                 y=180)
            else:
                label = Label(root,
                              text=" ¡CONTRASEÑA INCORRECTA! ")
                label.place(x=420, y=280)
                label.config(fg="blue",  # Foreground
                             bg="gold",  # Background
                             font=("Ebrima", 13, "bold"))
        def hecho2():
            nombre=Nombre1.get()
            nombres = seleccionar_nombres(conexion, cursor)
            if nombre in nombres:
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root,
                              text="¿Desea activar el sistema de reproduccion musical \n basada en su estado de animo?")
                label.place(x=10, y=20)
                label.config(fg="blue",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 19, "bold"))
                b4 = Button(root, relief="ridge", overrelief="flat", command=s2, width=80, height=80,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(
                    x=260, y=140)
                b5 = Button(root, relief="ridge", overrelief="flat", command=n2, width=80, height=80,anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400,y=140)
            else:
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root,
                              text="Ese usuario no se encuentra en la base de datos.")
                label.place(x=10, y=20)
                label.config(fg="blue",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))

                Volver = Button(root, text="volver", relief="ridge", overrelief="flat", command=hecho, width=10,
                            height=1,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=600, y=320) 
        def s2():
            nombre = Nombre1.get()
            musica = 1
            list = root.place_slaves()
            for l in list:
                l.destroy()
            Conexion().actualizar(conexion, cursor, nombre, nombre, musica)
            label = Label(root,
                              text="Se actualizo a"+ nombre)
            label.place(x=10, y=20)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))
                

        def n2():
            nombre = Nombre1.get()
            musica = 0
            list = root.place_slaves()
            for l in list:
                l.destroy()
            Conexion.actualizar(conexion, cursor, nombre, nombre, musica)
            label = Label(root,
                              text="Se actualizo a"+ nombre)
            label.place(x=10, y=20)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))

        def ayuda():
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                          text="• Usuarios registrados: Esta opción le muestra al usuario todos los nombres de las personas que ya están registradas.")
            label.place(x=0, y=10)
            label2 = Label(root,
                           text="• Actualizar usuario: Esta opción le permite al usuario seleccionar a cualquier usuario registrado y modificar si desea activar")
            label2.place(x=0, y=30)
            label3 = Label(root, text="la música o no cuando este sonriendo.")
            label3.place(x=0, y=50)
            label4 = Label(root,
                           text="• Acerca del sistema: Este botón le brinda información al usuario sobre las partes importantes del sistema y para qué sirve")
            label4.place(x=0, y=70)
            label5 = Label(root,
                           text="• Ayuda: Este botón le brinda instrucciones de cómo utilizar el sistema y le da información de cómo utilizar los botones")
            label5.place(x=0, y=90)
            label.config(fg="black",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 9))
            label2.config(fg="black",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label3.config(fg="black",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label4.config(fg="black",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label5.config(fg="black",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
        def acerca():
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                          text="Este es un sistema de monitoreo al conductor en un vehículo automóvil mediante visión artificial; el sistema consta ")
            label.place(x=0, y=45)
            label2 = Label(root,
                           text="principalmente de una computadora (Raspberry Pi 4) y una cámara incorporada al retrovisor del automóvil. La finalidad")
            label2.place(x=0, y=65)
            label3 = Label(root,
                           text="del sistema es, en el ámbito de la seguridad, obtener imágenes en tiempo real del conductor para determinar si éste se")
            label3.place(x=0, y=85)
            label4 = Label(root,
                           text="encuentra hablando por celular mientras conduce, esto se logra analizando la imagen obtenida por la cámara y")
            label4.place(x=0, y=105)
            label5 = Label(root,
                           text="determinando si aparece o no el celular en ella. Si el celular es detectado durante un tiempo determinado, el sistema")
            label5.place(x=0, y=125)
            label6 = Label(root,
                           text="emitirá una alarma sonora (además de una visual), que se apagará automáticamente si y solo si el celular deja de aparecer")
            label6.place(x=0, y=145)
            label7 = Label(root,
                           text="en la imagen, pero aumentará su intensidad en caso de que esté siga apareciendo; además, se limitará la aceleración")
            label7.place(x=0, y=165)
            label8 = Label(root,
                           text="permitida bloqueando la lectura del sensor del pedal del acelerador.")
            label8.place(x=0, y=185)
            label9 = Label(root,
                           text="El sistema tambien reconoce el rostro del usuario y cuando sonrie reproduce la musica feliz si usted lo desea.")
            label9.place(x=0, y=205)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 9))
            label2.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label3.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label4.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label5.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label6.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label7.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label8.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
            label9.config(fg="blue",  # Foreground
                          bg="silver",  # Background
                          font=("Ebrima", 9))
        #//////////////////////////////////////////////////////MAIN\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        Label(root, image=Imagen1, bd=5).pack(side="bottom")

        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label="Usuarios registrados",command=lista_usr)
        filemenu.add_command(label="Modificar Usuarios",command=actualizar_usuario)
        
        menubar.add_cascade(label="Opciones", menu=filemenu)
        menubar.add_command(label="Acerca del sistema", command=acerca)
        menubar.add_command(label="Ayuda",command=ayuda)
        root.config(menu=menubar)
        
            
        if nombre is not None:
            nombre_carpeta = nombre
            nombre_carpeta = nombre_carpeta.lower()
            def close_window():
                root.destroy()
            
            if self.comprobar(nombre_carpeta, conexion, cursor):
                nombre, validar_musica = Conexion().seleccionar_musica(conexion, cursor, nombre)
                label = Label(root, text="Que tenga un excelente viaje " + nombre)
                label.place(x=160, y=50)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))
                cerrar = Button(root, text="cerrar", relief="ridge", overrelief="flat", command=close_window, width=10,
                                height=1,
                                anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=320)
                root.mainloop()
                return nombre, validar_musica
        
        else:
            def close():
                root.destroy()
                detectar_celulares()
            
            def preguntar():
                list2 = root.place_slaves()
                for l in list2:
                    l.destroy()
                label = Label(root, text="Este usuario no se encuentra en la base de datos\n\n¿Desea agregarlo como un conductor?")
                label.place(x=10, y=10)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))
                b4 = Button(root, relief="ridge", overrelief="flat", command=si, width=80, height=80,
                                anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(
                        x=260, y=140)
                b5 = Button(root, relief="ridge", overrelief="flat", command=no, width=80, height=80,
                                anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400,y=140)
            def si():
                list2 = root.place_slaves()
                for l in list2:
                    l.destroy()
                label = Label(root, text="De acuerdo. Ahora, solicitaremos algunos datos.")
                label.place(x=20, y=10)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))
                label = Label(root, text="Digite el password del superusuario")
                label.place(x=140, y=80)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))
                entry = Entry(root, width=20, textvariable=Contraseña, show="*", bd=18, justify="center")
                entry.place(x=276, y=180)
                b7 = Button(root, text="listo", relief="ridge", overrelief="flat", command=listo, width=10, height=2,
                        anchor="center",
                        bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=500, y=180)
            def no():
                
                list2 = root.place_slaves()
                for l in list2:
                    l.destroy()
                label = Label(root, text="Entendido, accesando como usuario desconocido.")
                label.place(x=10, y=40)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 20, "bold"))
                cerrar_ = Button(root, text="cerrar", relief="ridge", overrelief="flat", command=close, width=10,
                                height=1,
                             anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=340)
                Volver = Button(root, text="volver", relief="ridge", overrelief="flat", command=preguntar, width=10,
                            height=1,
                             anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=280)

              
            def listo():
                password2 = Contraseña.get()
                
                
                if password2 == password:
                    list = root.place_slaves()
                    for l in list:
                        l.destroy()
                    label = Label(root, text="¿Cual es su nombre?")
                    label.place(x=190, y=100)
                    label.config(fg="red",  # Foreground
                                 bg="silver",  # Background
                                 font=("Ebrima", 24, "bold"))
                    Entry(root, width=20, fg="black", textvariable=Nombre1, bd=18, justify="center").place(x=276, y=180)
                    b3 = Button(root, text="listo", relief="ridge", overrelief="flat", command=listo2, width=10, height=2,
                                anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36, fg="black").place(x=490,
                                                                                                                     y=180)
                else:
                    label = Label(root,
                                  text=" ¡CONTRASEÑA INCORRECTA! ")
                    label.place(x=420, y=280)
                    label.config(fg="blue",  # Foreground
                                 bg="gold",  # Background
                                 font=("Ebrima", 13, "bold"))
            
            def listo2():
                nombre=Nombre1.get()
                nombre_carpeta = nombre.lower()
                if self.comprobar(nombre_carpeta, conexion, cursor):
                    list = root.place_slaves()
                    for l in list:
                        l.destroy()
                        
                    label = Label(root,
                              text="Este usuario ya existe ")
                    label.place(x=190, y=110)
                    label.config(fg="blue",  # Foreground
                                 bg="silver",  # Background
                                 font=("Ebrima", 24, "bold"))
                    b7 = Button(root, text="Volver", relief="ridge", overrelief="flat", command=listo, width=10, height=2,
                        anchor="center",
                        bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=318, y=180)
                    
                else:
                    list = root.place_slaves()
                    for l in list:
                        l.destroy()
                    label = Label(root,
                                  text="¿Desea activar el sistema de reproduccion musical \n basada en su estado de animo?")
                    label.place(x=10, y=20)
                    label.config(fg="blue",  # Foreground
                                 bg="silver",  # Background
                                 font=("Ebrima", 19, "bold"))
                    b4 = Button(root, relief="ridge", overrelief="flat", command=si2, width=80, height=80,
                                anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(
                        x=260, y=140)
                    b5 = Button(root, relief="ridge", overrelief="flat", command=no2, width=80, height=80,
                                anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400,y=140)
            
            def si2():
                nombre = Nombre1.get()
                musica = 1
                Conexion().insertar(conexion, cursor, nombre, musica)
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root,
                              text="Coloquese frente a la camara para registrarlo \n\n la camara se activara en 10 segundos \ndespues de que presione 'listo' ")
                label.place(x=13, y=5)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 21, "bold"))
                b5 = Button(root, text="listo", font=helv36, relief="ridge", overrelief="flat", command=acabamos, width=15,
                            height=5,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=590, y=280)

            def no2():
                nombre = Nombre1.get()
                musica = 0
                Conexion().insertar(conexion, cursor, nombre, musica)
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                label = Label(root,
                              text="Coloquese frente a la camara para registrarlo \n\n la camara se activara en 10 segundos \ndespues de que presione 'listo' ")
                label.place(x=13, y=5)
                label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 21, "bold"))
                b5 = Button(root, text="listo", font=helv36, relief="ridge", overrelief="flat", command=acabamos, width=15,
                            height=5,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black").place(x=590, y=280)
            def acabamos():
                sleep(10)
                nombre = Nombre1.get()
                nombre_carpeta=nombre.lower()
                self.crear(nombre_carpeta)
                self.obtener_fotografias(nombre_carpeta)   
                self.entrenar(nombre_carpeta, n_usuario)
                
                list = root.place_slaves()
                for l in list:
                    l.destroy()
                list2 = root.pack_slaves()
                for l in list2:
                    l.destroy()    
                label = Label(root,
                              text="Terminamos \n ¡Buen viaje!")
                label.place(x=280, y=30)
                label.config(fg="blue",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 24, "bold"))
                Label(root, image=Imagen4, bd=5).place(x=300, y=180)
                cerrar = Button(root, text="cerrar", relief="ridge", overrelief="flat", command=close_window, width=10,
                                height=1,
                                anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=320)
                
            def close_window():
                root.destroy()
            preguntar()    
            root.mainloop()
         
                
                    
            
            nombre = Nombre1.get()
            nombre, validar_musica = Conexion().seleccionar_musica(conexion, cursor, nombre)
            return nombre, validar_musica
        def close_window():
            root.destroy()
         
if __name__ == '__main__':
    password = ""
    first = None
    Reconocedor = reconocimiento_facial()
    conexion, cursor = reconocimiento_facial().inicializar_DB()

    #Primera parte del programa, reconoce y almacena usuarios en una base de datos.
    try: 
        #Si el documento ya fue creado, no causará excepción. NO ES LA PRIMERA EJECUCIÓN
        with open("SU.txt", "r") as f:
            lineas = f.readlines()
            password = lineas[1]
            first = False

    except:
        #Significa que el archivo SU (Super Usuario) no ha sido creado.
        first = True
        
    if first is True:  
        nombre, musica = Reconocedor.primera_ejecucion(conexion, cursor)
        Reconocedor.cerrar_DB(conexion, cursor)
        
    else:
         nombre, musica = Reconocedor.reconocer(conexion, cursor, password)
         Reconocedor.cerrar_DB(conexion, cursor)
          
         
