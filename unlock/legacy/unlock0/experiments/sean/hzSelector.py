"""
Selects the 4 best frequencies from an SSVEP sweep training run.
"""

import numpy as np
import scipy.signal as sigfilt
import matplotlib.pyplot as plt
import sys
from fileparser import fileParser

class FreqSelector():

    def __init__(self,subject_id,run_timestamp):

        # KEY PARAMETERS
        trialSampOffset = 128   # 128 = 0.5 seconds
        trialCutLen     = 4.0   # n secs to cut from each trial
        lpass           = 5.0   # low hz cutoff for Butterworth filter
        hpass           = 45.0  # high hz cutoff for Butterworth filter
        butterOrder     = 4     # nth order Butterworth filter (usually 4th order)
        self.ffWin      = 0.1   # Fundamental frequency PSD window
        self.h1Win      = 0.1   # First harmonic PSD window

        # [0] trial number, [1] current run time, [2] current attend direction, and [3,4,5] EEG data
        fileDir         = "/Users/slorenz/Desktop/EEGDATA/"
#        self.all_data   = fileParser(fileDir+subject_id+'/sweep_runData_'+subject_id+'_'+run_timestamp+'.txt')
#        self.all_data   = self.all_data.transpose()
#        self.eeg_data   = self.all_data[3:6,:]

        # loads each trial's 4 display frequencies
        self.trials     = fileParser(fileDir+subject_id+'/sweep_runFreqs_'+subject_id+'_'+run_timestamp+'.txt')

        # other variables
        fs              = 256                   # sampling rate
        self.nElecs     = 3                     # n electrodes used (O1,Oz,O2)
        self.nSamples   = fs*trialCutLen        # number of samples to take per trial (the LFFT, basically)
        self.nfft       = self.nextpow2(self.nSamples) # FFT next power of 2 length
        [self.b,self.a] = sigfilt.butter(butterOrder,np.divide([lpass,hpass],fs/2),btype='bandpass')
        self.f          = fs/2*np.linspace(0,1,self.nfft/2+1) # frequency linspace
        self.nTrials    = int(self.all_data[0,-1])  # number of total trials
        self.hsdMatrix  = np.zeros((4,self.nTrials))
        self.hz_list    = np.unique(self.trials) # the list of frequencies shown

        # Get the sample number start points for each trial
        self.trialStartSample = []
        for i in range(self.nTrials):
            tempIdxVector = np.where(self.all_data[0,:] == i)
            self.trialStartSample.append(tempIdxVector[0][0] + trialSampOffset)

    def preproc(self,trial_data):
        """ Raw EEG trial segmen preprocessing steps (zero-mean and 4th order Butter filter) """
        self.y = np.zeros((self.nElecs,self.nSamples))               # Vector initialization
        for e in range(self.nElecs):
            self.y[e,:] = trial_data[e,:] - np.mean(trial_data[e,:]) # Zero-mean raw data
            self.y[e,:] = sigfilt.lfilter(self.b,self.a,self.y[e,:]) # Butterworth filter z-m data

    def nextpow2(self,i):
        """Grabs the next power of two for FFT"""
        n = 2
        while n < i: n = n * 2
        return n

    def trialFFT(self):
        self.yy = np.zeros((self.nElecs,self.nfft))
        for e in range(self.nElecs):
            self.yy[e,:] = abs(np.fft.fft(self.y[e,:],self.nfft))

    def harmFreqFinder(self,tempWin):
        """ Finds actual freq window value from yy. Gets used in freqWins """
        winsF = np.zeros((2,2))
        for i in range(0,2):
            for j in range(0,2):
                temp1 = abs(self.f-tempWin[i][j]); temp1=np.where(temp1==min(temp1))
                winsF[i][j] = int(temp1[0])
        return winsF

    def freqWins(self,trialStimFreqs):
        """Selects values from a small window around each stimulating frequency in PSD space"""
        self.winsF=np.zeros((4,2,2)) # winsF creates upper and lower windows for each stim freq
        for i in range(4):
            tempWin  = [[trialStimFreqs[i]-self.ffWin,trialStimFreqs[i]+self.ffWin], \
                        [2*trialStimFreqs[i]-self.h1Win,2*trialStimFreqs[i]+self.h1Win]]
            self.winsF[i,:,:] = self.harmFreqFinder(tempWin)

    def harmSum(self):
        """ HarmMeanFF (and H1) look at PSD values over and the mean over the window. This
            is done for all electrodes. Chose the mean axis wisely!! """
        self.harmSumOut = np.zeros(4)
        for i in range(4):
            tempWinsF  = self.winsF[i,:]
            harmMeanFF = np.mean(self.yy[:,tempWinsF[0][0]:tempWinsF[0][1]+1],axis=1)
            harmMeanH1 = np.mean(self.yy[:,tempWinsF[1][0]:tempWinsF[1][1]+1],axis=1)
            self.harmSumOut[i] = np.mean(harmMeanFF+harmMeanH1)

    def run(self):

        # you gotsta initialize! improvise! materialize!
        winners_hz      = []
        winners_count   = []
        losers_hz       = []
        losers_count    = []

        # Cycle through each trial
        for trial in range(self.nTrials):
            # load up the raw data for the trial
            trial_data = self.eeg_data[:,self.trialStartSample[trial]:self.trialStartSample[trial]+self.nSamples]

            # process it
            self.preproc(trial_data)
            self.trialFFT()
            self.freqWins(self.trials[:,trial])
            self.harmSum()

            # add it to the matrix of outputs
            self.hsdMatrix[:,trial] = self.harmSumOut

            # pick winners and losers
            hsdPick     = self.hsdMatrix[:,trial].argmax()
            groundTruth = int(self.all_data[2,self.trialStartSample[trial]])
            if hsdPick == groundTruth:
                winners_hz.append(self.trials[groundTruth,trial])
            else:
                losers_hz.append(self.trials[groundTruth,trial])

        # get number of times each frequency wins or loses; and get count of each attended Hz shown
        for hz in self.hz_list:
            winners_count.append(winners_hz.count(hz))
            losers_count.append(losers_hz.count(hz))

        # pick top 4 winners
        sorted_winners = np.array(winners_count).argsort()[::-1]
        top_four_winners = self.hz_list[sorted_winners[0:4]]
        next_four_winners = self.hz_list[sorted_winners[4:8]]
        print "The top four frequencies are: ", top_four_winners
        print "The next four frequencies are: ", next_four_winners

            # plot it
#            plt.plot(self.f[0:len(self.f)-1],self.yy[0,0:512])
#            plt.xlim(5,25)
#            plt.show()

if __name__ == "__main__":

    freqSelect = FreqSelector(sys.argv[1],sys.argv[2]) #argv[1]=Subject ID and argv[2]=run time stamp
    freqSelect.run()
