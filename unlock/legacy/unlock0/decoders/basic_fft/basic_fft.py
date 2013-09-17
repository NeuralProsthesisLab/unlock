import numpy as np
import scipy.signal as sigfilt
#import matplotlib.pyplot as plt

class basic_fft():
    def __init__(self):

        # KEY PARAMETERS
        trialLen        = 4.0   # n secs to cut from each trial
        lpass           = 8.0   # low hz cutoff for Butterworth filter
        hpass           = 34.0  # high hz cutoff for Butterworth filter
        butterOrder     = 4     # nth order Butterworth filter (usually 4th order
        self.care_freq  = 30

        # other variables
        fs              = 256                   # sampling rate
        self.nElecs     = 3                   # n electrodes used (O1,Oz,O2)
        self.nSamples   = fs*trialLen        # number of samples to take per trial (the LFFT, basically)
        self.nfft       = self.nextpow2(self.nSamples) # FFT next power of 2 length
        [self.b,self.a] = sigfilt.butter(butterOrder,np.divide([lpass,hpass],fs/2),btype='bandpass')
        #self.f          = fs/2*np.linspace(0,1,self.nfft/2+1) # frequency linspace for PLOTTING
        self.f          = np.fft.fftfreq(self.nfft, 1./fs)[:self.nfft/2]

    def preproc(self,trial_data):
        """ Raw EEG trial segmen preprocessing steps (zero-mean and 4th order Butter filter) """
        self.y = np.zeros((self.nElecs,self.nSamples))               # Vector initialization
        for e in range(self.nElecs):
            self.y[e,:] = sigfilt.lfilter(self.b,self.a,trial_data[e,:]) # Butterworth filter z-m data

    def nextpow2(self,i):
        """Grabs the next power of two for FFT"""
        n = 2
        while n < i: n = n * 2
        return n
#
#    def freqs(self):
#        return self.f

    def trialFFT(self):
        self.yy = np.zeros((self.nElecs,self.nfft))
        for e in range(self.nElecs):
#            self.yy[e,:] = abs(np.fft.fft(self.y[e,:],self.nfft))
            self.yy[e,:] = -20*np.log10(abs(np.fft.fft(self.y[e,:],self.nfft)))

#    def plotting(self,yy):
#        for i in range(yy.shape[0]):
#            plt.plot(self.f[0:len(self.f)-1],yy[i,0:512])
#        plt.xlim(10,17)
#        plt.show()

    def run(self,data):
        self.preproc(data)
        self.trialFFT()
        yy = self.yy

        return yy[:,0:512]

#        dataset=[0]*len(yy)
#        for i in range(yy.shape[0]):
#            dataset[i]=[self.f[0:len(self.f)-1],yy[i,0:512]]
#           dataset[i]=y[i,0:512]#[self.f[0:512],yy[i,0:512]]

#        self.do_we_care=np.nonzero(self.f <= self.care_freq)
#        how_much_care=len(self.do_we_care)
#        care_this_much=yy[:,0:how_much_care]
#



if __name__ == "__main__":

    fftstuff = fftStuff()
    fftstuff.run()
