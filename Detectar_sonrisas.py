# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 13:52:59 2020

@author: anton
"""
import cv2 as cv

clasificador_rostros = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
clasificador_sonrisas = cv.CascadeClassifier('haarcascade_smile.xml')
clasificador_celulares = cv.CascadeClassifier('Phone_Cascade.xml')

if clasificador_rostros.empty():
    raise IOError('No se ha encontrado el clasificador de rostros.')
if clasificador_sonrisas.empty():
    raise IOError('No se ha encontrado el clasificador de sonrisas.')
if clasificador_celulares.empty():
    raise IOError('No se ha encontrado el clasificador de celulares.')
    
def comprobar_uso():
    usando = True
    print("Por favor concentrece en el camino, suelte su telefono celular.")
    cap = cv.VideoCapture(0)
    while(usando):
        cel = 50
        
        while(cap.isOpened()):
            _, f = cap.read()
                    
            gray = cv.cvtColor(f, cv.COLOR_BGR2GRAY)
            celulares = clasificador_celulares.detectMultiScale(gray, 3, 9)
                
            if celulares == ():
                cel -= 1
                print(cel)
                    
            if cel == 0:
                usando = False
                cap.release()
                cv.destroyAllWindows()
                break
            
            for (cx, cy, cw, ch) in celulares:
                cv.rectangle(f, (cx,cy), (cx+cw, cy+ch), (255, 0, 255), 2)
                
            cv.imshow("Usando el celular", f)
            
            k = cv.waitKey(1)
            if k == 27:
                cap.release()
                cv.destroyAllWindows()
                break
        #Inicia nuevamente la busqueda de celulares    
        detectar_sonrisas()   
    
def detectar_sonrisas():      
    capture = cv.VideoCapture(0)
    contador_sonrisas = 0
    contador_celulares = 0
    
    while(capture.isOpened()):
        ret, frame = capture.read()
        
        if not ret:
            break
        
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        rostros = clasificador_rostros.detectMultiScale(gray, 1.3, 5)
        celulares = clasificador_celulares.detectMultiScale(gray, 15, 15)
        
        #DETECCION DE SONRISAS
        for (x, y, w, h) in rostros:
            cv.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)
            roi_color = frame[y:y+h, x:x+w]
            roi_gray = gray[y:y+h, x:x+w]
            
            sonrisas = clasificador_sonrisas.detectMultiScale(roi_gray, 1.2, 15)
            
            if sonrisas != ():
                print(contador_sonrisas)
                contador_sonrisas += 1
                
            if contador_sonrisas > 20:
                capture.release()
                cv.destroyAllWindows()
                return True
            
            for (sx, sy, sw, sh) in sonrisas:
                cv.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 0, 255), 3)
                
        #DETECCION DE CELULARES
        if celulares != ():
            print(contador_celulares)
            contador_celulares += 1
            
        if contador_celulares > 20:
            contador_celulares = 0
            break
        
        for (x, y, w, h) in celulares:
            cv.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
        
        cv.imshow("Reconocimiento de sonrisas", frame)
        
        k = cv.waitKey(1)
        if k == 27:
            break
        
    capture.release()
    cv.destroyAllWindows()
    comprobar_uso()

if __name__ == '__main__':
    detectar_sonrisas()