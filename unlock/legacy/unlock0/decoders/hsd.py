""" Decoder class for harmonic sum decision (HSD). HSD takes an FFT and pulls out a
window over the fundamental frequency and first harmonic of each stimulating SSVEP
frequency. It then """

import numpy as np
import scipy.signal as sigfilt

__author__ = "Sean Lorenz"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "0.1"
__email__ = "npl@bu.edu"
__status__ = "Development"

class HSD:
    
    # Set some power spectrum parameters
    def __init__(self,fs,tSecs,lpass,hpass):
        lfft            = fs*tSecs            # signal length
        self.nfft       = self.nextpow2(lfft) # FFT next power of 2 length
        [self.b,self.a] = sigfilt.butter(4,np.divide([lpass,hpass],fs/2),btype='bandpass')
        self.f          = fs/2*np.linspace(0,1,self.nfft/2+1) # frequency linspace

    # Selects values from a small window around each stimulating frequency in PSD space
    def freqWins(self,stimHz,ffWin,h1Win):
        winsF=np.zeros((len(stimHz),2,2)) # winsF creates a 3D matrix!
        for i in range(len(stimHz)):#Sean, I made an edit here 4-->len(stimHz): Dante
            tempWin  = [[stimHz[i]-ffWin,stimHz[i]+ffWin],[2*stimHz[i]-h1Win,2*stimHz[i]+h1Win]]
            winsF[i,:,:] = self.harmFreqFinder(self.f,tempWin)
        return winsF

    def nextpow2(self,i):
        n = 2
        while n < i: n = n * 2
        return n
        
    # Finds actual freq window value from yy. Gets used in freqWins 
    def harmFreqFinder(self,f,wins):
        winsFout = np.zeros((2,2))
        for i in range(0,2):
            for j in range(0,2):
                temp1 = abs(f-wins[i][j]); temp1=np.where(temp1==min(temp1))
                winsFout[i][j] = int(temp1[0])
        return winsFout
        
    # Raw EEG trial segmen preprocessing steps (zero-mean and 4th order Butter filter)
    def preproc(self,yVector):
        trialSeg = np.zeros(len(yVector))                  # Vector initialization
        trialSeg = yVector - np.mean(yVector)              # Zero-mean raw data
        trialSeg = sigfilt.lfilter(self.b,self.a,trialSeg) # Butterworth filter z-m data
        return trialSeg
    
    # HarmMeanFF (and H1) look at PSD values over and the mean over the window. This 
    # is done for all electrodes. Chose the mean axis wisely!!
    def harmSum(self,winsf,yy):
        harmMeanFF = np.mean(yy[:,winsf[0][0]:winsf[0][1]+1],axis=1)
        harmMeanH1 = np.mean(yy[:,winsf[1][0]:winsf[1][1]+1],axis=1)
        harmSumOut = np.mean(harmMeanFF+harmMeanH1)
        return harmSumOut
