from decoders import HSD, CCA
import functionGenerator
import numpy as np

class fft_Decoder():
    def __init__(self, fs=256, dur=2, stimHz=[12,13,14,15], ffWin=0.1, h1Win=0.1, lpass=8.0, hpass=34.0):
        self.h       = HSD(fs, dur, lpass, hpass)
        self.f       = self.h.f
        self.nfft    = self.h.nfft

        self.numsamp = fs*dur
        self.winsF   = self.h.freqWins(stimHz, ffWin, h1Win)

    def decode(self, y, mag):
        Y   = np.zeros(self.numsamp)
        trialSeg = self.h.preproc(y)        # Trial segment signal preprocessing
        if   mag == 'abs':
            Y[:]  = np.abs(np.fft.fft(trialSeg,self.nfft)) # abs of FFT
        elif mag == 'dB':
            Y[:]  = 10*np.log(abs(np.fft.fft(trialSeg,self.nfft))) # abs of FFT

        return Y

    def classify(self,Y):
        harmSums=np.zeros(len(stimHz))
        for i in range(len(stimHz)):
            harmSums = self.h.harmSum(self.winsF[i,:],Y)
        guessInd = harmSums.argmax()
        guess = stimHz(guessInd)
        return [guess, guessInd]


class cca_decoder():
    def __init__(self, fs=256, dur=2, stimHz=[12,13,14,15], numchan=1,lpass=8.0, hpass=34.0):

        cca=CCA(self.fs, self.dur, lpass, hpass)

        self.fs=fs
        self.dur=dur
        self.stimHz=stimHaz
        self.numchan = numchan
        self.numfreq=len(self.stimHz)
        numsamp = dur*fs

        self.templates = np.zeros(numfreq,numsamp)

        for i in range(numFreq):
            func = functionGenerator(frequency=self.stimHz[i], fs=self.fs, dur=self.dur)
            self.templates[i]= func.sendto_file()



    def decode(self,seg):
        dec
        for i in range(self.numchan):
            R = np.zeros(self.numfreq)
            X = cca.preproc(seg[i,:])
            for j in range(self.numfreq):
                Wx,Wy,R[j] = cca.cca(X,self.templates[j])




                Wx,Wy,Rd = cca.cca(X,Yd)
                Wx,Wy,Rl = cca.cca(X,Yl)
                Wx,Wy,Rr = cca.cca(X,Yr)
                allR     = [Ru[0],Rd[0],Rl[0],Rr[0]]
                ccaWinner = np.argsort(allR)[3]+1









