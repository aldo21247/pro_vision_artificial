# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 15:55:19 2020

@author: anton
"""
import cv2 as cv

clasificador_celulares = cv.CascadeClassifier('Phone_Cascade.xml')

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
            celulares = clasificador_celulares.detectMultiScale(gray, scaleFactor = 17,minNeighbors=191, minSize=(270,78))
                
            if celulares == ():
                cel -= 1
                print(cel)
                    
            if cel == 0:
                usando = False
                cap.release()
                cv.destroyAllWindows()
                break
            
            for (cx, cy, cw, ch) in celulares:
                cv.rectangle(f, (cx,cy), (cx+cw, cy+ch), (0, 0, 255), 2)
                
            cv.imshow("Usando el celular", f)
            
            k = cv.waitKey(1)
            if k == 27:
                cap.release()
                cv.destroyAllWindows()
                break
        #Inicia nuevamente la busqueda de celulares    
        detectar_celulares()

def detectar_celulares():
    capture = cv.VideoCapture(0)
    contador_celulares = 0
    
    while(capture.isOpened()):
        ret, frame = capture.read()
        
        if not ret:
            break
        
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        celulares = clasificador_celulares.detectMultiScale(gray, 3, 9)
        
        if celulares != ():
            print(contador_celulares)
            contador_celulares += 1
            
        if contador_celulares > 20:
            contador_celulares = 0
            break
        
        for (x, y, w, h) in celulares:
            cv.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 255), 2)
        cv.imshow("Reconocimiento de celulares", frame)
        
        k = cv.waitKey(1)
        if k == 27:
            break
    
    capture.release()
    cv.destroyAllWindows()    
    comprobar_uso()
        
if __name__ == '__main__':
    detectar_celulares()