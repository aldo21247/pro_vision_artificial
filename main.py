


from GUI import Reproductor
from Base_datos import Conexion
import tkinter.font as tkFont
import cv2 as cv
from Reconocimiento_Facial import reconocimiento_facial
from Detectar_sonrisas import detectar_sonrisas
from Detectar_celulares import detectar_celulares
from tkinter import *
import threading

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
     
#Segunda parte del programa, se ejecuta todo el tiempo, detecta las sonrisas
#y si estás superan un limite, se reproduce automáticamente la musica     
     
if not musica:
    detectar_celulares()     
     

else:    
    if detectar_sonrisas():
        
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
        conexion = Conexion().create_connection()
        cursor = conexion.cursor()
        helv36 = tkFont.Font(family='Arial', size=9, weight="bold")
        Imagen1 = PhotoImage(file="robot.gif")
        Imagen2 = PhotoImage(file="si.png")
        Imagen3 = PhotoImage(file="no.png")
        
        #//////////////////////////////////////////////////////FUNCIONES\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        def activar_musica():
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root, text="¡Notamos que esta feliz!\n ¿Quiere reproducir la musica feliz?")
            label.place(x=65, y=10)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 24, "bold"))
            b1 = Button(root, relief="ridge", overrelief="flat", command=si, width=80, height=80,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", fg="black", image=Imagen2).place(x=260, y=140)
            b2 = Button(root, relief="ridge", overrelief="flat", command=no, width=80, height=80,
                        anchor="center", bg="red", bd=10, cursor="hand2", fg="black", image=Imagen3).place(x=400, y=140)
            
        
        def si():
            list = root.place_slaves()
            for l in list:
                l.destroy()
            reproductor = Reproductor(root)
            root.protocol("WM_DELETE_WINDOW", root.iconify)
            root.bind('<Escape>', lambda e: reproductor.OnClose())
        
        
        def no():
            list = root.place_slaves()
            for l in list:
                l.destroy()
            label = Label(root,
                              text="No se activo la musica ")
            label.place(x=125, y=10)
            label.config(fg="red",  # Foreground
                             bg="silver",  # Background
                             font=("Ebrima", 30, "bold"))
            cerrar = Button(root, text="cerrar", relief="ridge", overrelief="flat", command=close_window, width=10,
                            height=1,
                            anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36).place(x=600, y=320)

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
                             font=("Ebrima", 20, "bold"))
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
            label = Label(root, text="¿Cual es el nombre del usuario que desea actualizar?")
            label.place(x=10, y=100)
            label.config(fg="red",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 18, "bold"))
            Entry(root, width=20, fg="black", textvariable=Nombre1, bd=18, justify="center").place(x=276, y=180)
            b3 = Button(root, text="listo", relief="ridge", overrelief="flat", command=hecho2, width=10, height=2,
                        anchor="center", bg="#38EB5C", bd=10, cursor="hand2", font=helv36, fg="black").place(x=490,
                                                                                                             y=180)
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

                Volver = Button(root, text="volver", relief="ridge", overrelief="flat", command=actualizar_usuario, width=10,
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
                              text="Se actualizo a "+ nombre)
            label.place(x=150, y=100)
            label.config(fg="blue",  # Foreground
                         bg="silver",  # Background
                         font=("Ebrima", 20, "bold"))
                

        def n2():
            nombre = Nombre1.get()
            musica = 0
            list = root.place_slaves()
            for l in list:
                l.destroy()
            Conexion().actualizar(conexion, cursor, nombre, nombre, musica)
            label = Label(root,
                              text="Se actualizo a "+ nombre)
            label.place(x=150, y=100)
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
                           text="• Actualizar usuario: esta opción le permite al usuario seleccionar a cualquier usuario registrado y modificar si desea activar")
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
                           text="permitida bloqueando la lectura del sensor del pedal del acelerador. El sistema tambien reconoce el rostro del usuario y cuando sonrie reproduce la musica feliz si usted lo desea.")
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
        th = threading.Thread(target = detectar_celulares) 
        th.setDaemon(True)
        th.start() 
        
    
        Label(root, image=Imagen1, bd=5).pack(side="bottom")
        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label="Usuarios registrados",command=lista_usr)
        filemenu.add_command(label="Modificar Usuarios",command=actualizar_usuario)
        
        menubar.add_cascade(label="Opciones", menu=filemenu)
        menubar.add_command(label="Acerca del sistema", command=acerca)
        menubar.add_command(label="Ayuda",command=ayuda)
        root.config(menu=menubar)
        activar_musica()
        root.mainloop()
        
        
