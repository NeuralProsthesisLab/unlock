from hsd import HSD
import pymotiv

import socket
import time
import numpy as np
import json

class SsvepDecoder:
    
    def __init__(self,tSecs,stimHz,UDP_IP,UDP_PORT):
        
        # PARAMETERS
        fs      = 128               # Sampling rate
        self.nElecs  = 2            # Number of electrodes used
        lpass   = min(stimHz)-2     # Low end of filter
        hpass   = 2*max(stimHz)+4   # High end of filter
        self.tLen = int(fs*tSecs)
        ffWin   = 0.1               # Harmonic window for fundamental
        h1Win   = 0.1               # Harmonic window for 1st harmonic
        self.exitLoop= False        # Keeps the main while loop going
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT
        self.y  = np.zeros((self.nElecs,self.tLen+32))
        self.yIdx = 0
        self.mu = 0
        self.eta = 0.05
        self.blinkThresh = 40#2200
        self.lastSample = 10000000000000
        self.eyeblink = False
        self.EYEBLINK_INTERVAL = 0.200
        self.DOUBLEBLINK = 1
        self.DOUBLEBLINK_INTERVAL = 2
        self.last_blink = time.time()+3
        
        # UDP SETTINGS
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.settimeout(0.001)
        self.sock2 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock2.settimeout(0.001)
        self.sock3 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock3.settimeout(0.001)
        self.sock4 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # incoming
        self.sock4.settimeout(0.001)
        self.sock4.bind(('127.0.0.1',33448))
        
        # GTEC DEVICE SETTINGS
        self.device = pymotiv.EPOC()
        isopen = self.device.open()
        isinit = self.device.init(1) # 120 = EOG+O1+Oz+O2+EOG 8+16+32+64
        isstarted = self.device.start()
        if isopen == 1: print 'okay! mobilab opened'
        if isinit == 1: print 'okay! mobilab initialized'
        if isstarted == 1: print 'okay! mobilab started!'
        
        # HSD SETTINGS
        self.h     = HSD(fs,tSecs,lpass,hpass)
        self.winsF = self.h.freqWins(stimHz,ffWin,h1Win)
        self.nfft  = self.h.nfft

    def run(self):

        while self.exitLoop == False:
            reset = None
            try:
                reset, _ = self.sock4.recvfrom(1)
            except socket.timeout:
                pass

            if reset is not None:
                print "RESET!"
                self.yIdx = 0

            samples = self.device.acquire()
            if not samples: continue
            # STEP 1: Grab data from mobilab            
            yEmotiv = self.device.getdata(3*samples)
            self.y[0,self.yIdx:self.yIdx+samples] = yEmotiv[0:samples]
            self.y[1,self.yIdx:self.yIdx+samples] = yEmotiv[samples:2*samples]
            #self.y[:,self.yIdx] = yGtec[1:4] # only grab O1,Oz,O2
            self.yIdx+=samples
            
            # STEP 2a: Eye blink
#            yEOG = 0
#            for s in yEmotiv[0:samples]:
#                yEOG = s
#                self.mu = self.mu*(1-self.eta) + self.eta*yEOG
#                yEOG -= self.mu
#
#
#            self.eyeblink = yEOG > self.blinkThresh and yEOG > self.lastSample
#            now = time.time()
#            if self.eyeblink:
#                if now - self.last_blink > self.EYEBLINK_INTERVAL:
#                    print 'blink'
#                    if now - self.last_blink < self.DOUBLEBLINK:
#                        print 'double blink [%.3f]' % now
#                        #self.sock2.sendto(str(1),('127.0.0.1',33446))
#                        self.last_blink = now + self.DOUBLEBLINK_INTERVAL
#                    else:
#                        self.last_blink = now
#            self.lastSample = yEOG

            # STEP 2: If buffer full, zero-mean, filter, and FFT.
            if self.yIdx >= self.tLen:
                yy = np.zeros((self.nElecs,self.nfft))            # Trial power spectrum initialization
                for j in range(self.nElecs):                      # Repeat for each electrode:
                    trialSeg = self.h.preproc(self.y[j,0:self.tLen])        # Trial segment signal preprocessing
                    yy[j,:]  = abs(np.fft.fft(trialSeg,self.nfft)) # abs of FFT
                
                # STEP 3: Harmonic sum decision (HSD)
                harmSums = np.zeros(4)
                for i in range(4):
                    harmSums[i] = self.h.harmSum(self.winsF[i,:],yy)
                
                # STEP 4: Pick the max value as winner and send UDP packet
                hsdPick = harmSums.argmax()+1 # add "1" if going 1-4 rather than 0-3
                print hsdPick
                self.sock.sendto(str(hsdPick),('127.0.0.1',33445))
                self.yIdx = 0
                self.y = np.zeros((self.nElecs,self.tLen+32))

            out = []
            for s in range(samples):
                AF3 = str(yEmotiv[2*samples + s] - 5000)
                O1 = str(yEmotiv[s] - 5000)
                O2 = str(yEmotiv[samples + s] - 5000)

                x = [AF3,O1,O2]
                self.sock3.sendto(json.dumps(x),('127.0.0.1',33447))
        # TURN OFF THE MOBILAB AFTER RUN COMPLETE.
        self.d.stop()
        self.d.close()

if __name__=="__main__":

    # Make into a settings.py file! Then do from settings import *
    tSecs     = 4.0                         # 4.0 for HSD; 2.0 (or less ) for CCA
    stimHz    = [12.0, 13.0, 14.0, 15.0]    # Stimulating frequencies
    #stimHz    = [12.0, 13.5, 15.0, 16.5]
    UDP_IP    = '128.197.122.62'                 # UDP IP
    UDP_PORT  = 33445                       # UDP port

    proto = SsvepDecoder(tSecs,stimHz,UDP_IP,UDP_PORT)
    proto.run()
