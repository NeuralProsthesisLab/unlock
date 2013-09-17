from hsd import HSD
import pygtec

import socket
import time
import numpy as np
import json

class SsvepDecoder:
    
    def __init__(self,tSecs,stimHz,UDP_IP,UDP_PORT):

        # IMPORTANT SETTINGS
        com_port        = "/dev/rfcomm0"    # "COM3" usually for Mouth; "/dev/rfcomm0" for Linux
        self.blinkThresh= 4000      # Arbitrary blink threshold!!

        # HSD settings
        fs              = 256               # Sampling rate
        self.nElecs     = 3                 # Number of electrodes used
        lpass           = min(stimHz)-2     # Low end of filter
        hpass           = 2*max(stimHz)+4   # High end of filter
        self.tLen       = int(fs*tSecs)     # Number of trial length samples (1024 if 4s)
        ffWin           = 0.1               # Harmonic window for fundamental
        h1Win           = 0.1               # Harmonic window for 1st harmonic
        self.exitLoop   = False             # Keeps the main while loop going
        self.UDP_IP     = UDP_IP
        self.UDP_PORT   = UDP_PORT
        self.y          = np.zeros((self.nElecs,self.tLen))
        self.yIdx       = 0
        self.h          = HSD(fs,tSecs,lpass,hpass)
        self.winsF      = self.h.freqWins(stimHz,ffWin,h1Win)
        self.nfft       = self.h.nfft

        # EOG settings
        self.mu         = 0
        self.eta        = 0.05
        self.lastSample = 10000000000000
        self.eyeblink   = False
        self.EYEBLINK_INTERVAL = 0.200
        self.DOUBLEBLINK = 1
        self.DOUBLEBLINK_INTERVAL = 2
        self.last_blink = time.time()+3

        # UDP settings
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )  # outgoing
        self.sock.settimeout(0.001)
        self.sock2 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # outgoing
        self.sock2.settimeout(0.001)
        self.sock3 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # outgoing
        self.sock3.settimeout(0.001)
        self.sock4 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # incoming
        self.sock4.settimeout(0.001)
        self.sock4.bind(('127.0.0.1',33448))
        
        # GTEC settings
        self.device = pygtec.MOBIlab()
        isopen = self.device.open(com_port)
        isinit = self.device.init(120,0) # 120 = EOG+O1+Oz+O2+EOG 8+16+32+64
        isstarted = self.device.start()
        if isopen == 1: print 'okay! mobilab opened'
        if isinit == 1: print 'okay! mobilab initialized'
        if isstarted == 1: print 'okay! mobilab started!'

    def run(self):

        while self.exitLoop == False and self.device.acquire():
            reset = None
            try:
                reset, _ = self.sock4.recvfrom(1)
            except socket.timeout:
                pass

            if reset is not None:
                print "RESET!"
                self.yIdx = 0

            # STEP 1: Grab data from mobilab            
            yGtec = self.device.getdata(self.nElecs+1)
            self.y[:,self.yIdx] = yGtec[1:4] # only grab O1,Oz,O2
            self.yIdx+=1

            # STEP 2: Eye blink
            yGtecEOG = yGtec[0]
            self.mu = self.mu*(1-self.eta) + self.eta*yGtecEOG
            yGtecEOG -= self.mu

            self.eyeblink = (yGtecEOG > self.blinkThresh) and (yGtecEOG > self.lastSample)
            now = time.time()
            if self.eyeblink:
                if now - self.last_blink > self.EYEBLINK_INTERVAL:
                    print 'blink'
                    if now - self.last_blink < self.DOUBLEBLINK:
                        print 'double blink [%.3f]' % now
                        self.sock2.sendto(str(1),('127.0.0.1',33446))
                        self.last_blink = now + self.DOUBLEBLINK_INTERVAL
                    else:
                        self.last_blink = now
            self.lastSample = yGtecEOG

            # STEP 3: If buffer full, zero-mean, filter, and FFT.
            if self.yIdx == self.tLen:
                yy = np.zeros((self.nElecs,self.nfft))            # Trial power spectrum initialization
                for j in range(self.nElecs):                      # Repeat for each electrode:
                    trialSeg = self.h.preproc(self.y[j,:])        # Trial segment signal preprocessing
                    yy[j,:]  = abs(np.fft.fft(trialSeg,self.nfft)) # abs of FFT
#                    yy[j,:]  = 10*np.log(abs(np.f7ft.fft(trialSeg,self.nfft))) # abs of FFT

                # STEP 4: Harmonic sum decision (HSD)
                harmSums = np.zeros(4)
                for i in range(4):
                    harmSums[i] = self.h.harmSum(self.winsF[i,:],yy)
                
                # STEP 5: Pick the max value as winner and send UDP packet
                hsdPick = harmSums.argmax() + 1 # add "1" if going 1-4 rather than 0-3
                print hsdPick
                self.sock.sendto(str(hsdPick),('127.0.0.1',33445))
                self.yIdx = 0
                self.y = np.zeros((self.nElecs,self.tLen))
            
            self.sock3.sendto(json.dumps(yGtec.tolist()),('127.0.0.1',33447))
        # TURN OFF THE MOBILAB AFTER RUN COMPLETE.
        self.device.stop()
        self.device.close()

if __name__=="__main__":

    # Make into a settings.py file! Then do from settings import *
    tSecs     = 4.0                         # 4.0 for HSD; 2.0 (or less ) for CCA
    stimHz    = [12.0, 13.0, 14.0, 15.0]    # Stimulating frequencies
#    UDP_IP    = '128.197.122.62'            # UDP IP
    UDP_IP    = 'localhost'
    UDP_PORT  = 33445                       # UDP port

    proto = SsvepDecoder(tSecs,stimHz,UDP_IP,UDP_PORT)
    proto.run()
