__author__ = "Dante Smith"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "npl@bu.edu"
__status__ = "Development"

import pygame
import time
import numpy as np
import scipy.signal as sig
import random
import socket
import json
from testing import SpectrumScope
from testing import sqSSVEP
from testing import freqSelect
from testing import TimeScope

socket_data = socket.socket(type=socket.SOCK_DGRAM)
socket_data.settimeout(0.001)
socket_data.bind(('127.0.0.1',33447))

pygame.display.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

time_screen=screen.subsurface([(screen.get_width())/2,0],[(screen.get_width())/2,(screen.get_height())/2])
scope_screen=screen.subsurface([(screen.get_width())/2,(screen.get_height())/2], [(screen.get_width())/2,(screen.get_height())/2])

chan = 1
dur = 5
fs = 256

freqs = ['11.5','12.0', '12.5','13.0','13.5',
         '14.0','14.5','15.0','15.5','16.0']
n=2
## Initialize classes
stimulus = sqSSVEP(screen)
buttongrid = freqSelect(screen,freqs)
timeScope= TimeScope(time_screen,numchan=4,ylim=(-10000, 10000), duration=dur)
spectrum = SpectrumScope(scope_screen,chan,dur,fs)                                                        

Freq=0

running = True
old_time = time.time()
while running:
    data = []
    while True :
        try:
            d, _ = socket_data.recvfrom(64)
            data.append(json.loads(d))
        except socket.timeout:
            break
        
    screen.fill((0,0,0))
##    elapsed = time.time() - old_time
##    if elapsed >= 1.0:
##        spectrum.pushBuffer(sum(pushData(chan,fs,b,a),[]))
##        old_time = time.time()
##    time.sleep(1./256.)

    stimulus.update(float(Freq))
    stimulus.draw()

    buttongrid.draw()

    timeScope.sample(data)
    timeScope.draw()

    spectrum.sample(data)
    spectrum.draw()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1 :
                Freq=buttongrid.update(event.pos)
                #b,a = sig.butter(4,np.array([float(Freq)-.5,float(Freq)+.5])/128.,btype='bandpass')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.QUIT:
            running = False 

socket_data.close()
pygame.quit()
