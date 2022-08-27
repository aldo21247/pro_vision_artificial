# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:15:46 2020

@author: anton
"""
import os
from vlc import Instance
import tkinter as Tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from os.path import basename, expanduser, isfile, join as joined
from pathlib import Path
import time

class VLC:
    def __init__(self):
        self.Player = Instance()
    
    def MediaPlayer(self):
        self.media_player = self.Player.media_player_new()
        return self.media_player
        
    def Playlist(self):
        self.mediaList = self.Player.media_list_new()
        direccion = "./Feliz/"
        canciones = os.listdir(direccion)
        for c in canciones:
            self.mediaList.add_media(self.Player.media_new(joined(direccion,c)))
            
        self.listPlayer = self.Player.media_list_player_new()
        self.listPlayer.set_media_list(self.mediaList)
        return self.listPlayer
    
    def play(self):
        self.listPlayer.play()
        
    def next(self):
        self.listPlayer.next()
        
    def pause(self):
        self.listPlayer.pause()
        
    def previous(self):
        self.listPlayer.previous()
        
    def stop(self):
        self.listPlayer.stop()
        
    def get_instance(self):
        return self.player

    
class Reproductor(Tk.Frame):
    _stopped  = None
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        
        self.parent = parent  
        
        self.buttons_panel = Tk.Toplevel(self.parent)
        self.buttons_panel.protocol("WM_DELETE_WINDOW", parent.iconify)
        self.buttons_panel.bind('<Escape>', lambda e: self.OnClose())
        self.buttons_panel.title("Felicidad")
        self.is_buttons_panel_anchor_active = True

        #Botones PLAY, STOP, SIGUIENTE, ANTERIOR, MUTE Y VOLUMEN
        buttons = ttk.Frame(self.buttons_panel)
        self.playButton = ttk.Button(buttons, text="Play", command = self.Play)
        self.playButton.pack(side = Tk.LEFT)
        self.stopButton = ttk.Button(buttons, text="Stop", command = self.Stop)
        self.stopButton.pack(side=Tk.LEFT)
        self.nextButton = ttk.Button(buttons, text="Siguiente", command = self.Siguiente)
        self.nextButton.pack(side=Tk.LEFT)
        self.previousButton = ttk.Button(buttons, text="Anterior", command = self.Anterior)
        self.previousButton.pack(side=Tk.LEFT)
        self.muteButton = ttk.Button(buttons, text="Mute", command = self.Mute)
        self.muteButton.pack(side=Tk.LEFT)

        self.volMuted = False
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command = self.OnVolume,
                                  from_= 0, to = 100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue = 100, label='Volumen')
        self.volSlider.pack(side=Tk.RIGHT)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)
        
        timers = ttk.Frame(self.buttons_panel)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable = self.timeVar, command = self.OnTime,
                                    from_=0, to = 1000, orient=Tk.HORIZONTAL, length=500,
                                    showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.BOTTOM, fill=Tk.X)
        
        #VLC PARA REPRODUCCIÓN DE ARCHIVOS MEDIA
        self.vlc = VLC()
        self.player = self.vlc.Playlist() 
        self.Play()
        self.OnTick()

    def Play(self, *unused):
        # Try to play, if this fails display an error message
        if self.player.play() == -1:
            self.showError("Unable to play the video.")
        else:
            self._Pause_Play(True)
        # self.player.get_media_player().play() 
            # set volume slider to audio level
            vol = self.player.get_media_player().audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)
                
    def Pause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media_player():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  
        
    def _Pause_Play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.Play if playing is None else self.Pause
        self.playButton.config(text=p, command=c)
        self._stopped = False
        
    def Stop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player:
            self.player.stop()
            self._Pause_Play(None)
            # reset the time slider
            self.timeSlider.set(0)
            self._stopped = True
            
    def Siguiente(self):
        self.player.next()
        
    def Anterior(self):
        self.player.previous()
    
    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player.get_media_player():
            # since the self.player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.player.get_media_player().get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_media_player().get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        # start the 1 second timer again
        self.parent.after(1000, self.OnTick)
        # adjust window to video aspect ratio, done periodically
        # on purpose since the player.video_get_size() only
        # returns non-zero sizes after playing for a while
        
    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                # this is a hack. The timer updates the time slider.
                # This change causes this rtn (the 'slider has changed' rtn)
                # to be invoked.  I can't tell the difference between when
                # the user has manually moved the slider and when the timer
                # changed the slider.  But when the user moves the slider
                # tkinter only notifies this rtn about once per second and
                # when the slider has quit moving.
                # Also, the tkinter notification value has no fractional
                # seconds.  The timer update rtn saves off the last update
                # value (rounded to integer seconds) in timeSliderLast if
                # the notification time (sval) is the same as the last saved
                # time timeSliderLast then we know that this notification is
                # due to the timer changing the slider.  Otherwise the
                # notification is due to the user changing the slider.  If
                # the user is changing the slider then I have the timer
                # routine wait for at least 2 seconds before it starts
                # updating the slider again (so the timer doesn't start
                # fighting with the user).
                self.player.get_media_player().set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()
        
    def Mute(self, *unused):
        """Mute/Unmute audio.
        """
        # audio un/mute may be unreliable, see vlc.py docs.
        self.volMuted = m = not self.volMuted  
        self.player.get_media_player().audio_set_mute(m)
        u = "Unmute" if m else "Mute"
        self.muteButton.config(text=u)
        # update the volume slider text
        #self.OnVolume()
    
    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        v_M = "%d%s" % (vol, " (Muted)" if self.volMuted else '')
        self.volSlider.config(label="Volume " + v_M)
        if self.player and not self._stopped:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            # e.g. if the player is stopped or doesn't have media
            if self.player.get_media_player().audio_set_volume(vol):  # and self.player.get_media():
                self.showError("Failed to set the volume: %s." % (v_M,))
                
    def OnClose(self, *unused):
        """Closes the window and quit.
        """
        # print("_quit: bye")
        self.Stop()
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  
    
    def showError(self, message):
        """Display a simple error dialog.
        """
        self.Stop()
        showerror(self.parent.title(), message)
        
if __name__ == '__main__':
    
    reproductor = Reproductor(root)
    root.protocol("WM_DELETE_WINDOW", root.iconify)
    root.bind('<Escape>', lambda e: reproductor.OnClose())
     