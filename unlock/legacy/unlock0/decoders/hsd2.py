import numpy as np
#import pymutt
#import matplotlib.pyplot as plt

__author__ = "Sean Lorenz"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "npl@bu.edu"
__status__ = "Development"

class HSD2:

    def __init__(self, fs=256.0, dur=4.0, stimHz=[12,13,14,15],numchan=3,
                 ff_window=0.1,h1_window=0.1,mtp_npi=1.0,mtp_nwin=4,psd_method='mtp',file_baseline=''):
        """ Set some power spectrum parameters
        """
        self.stimHz             = stimHz                            # SSVEP frequencies used for display
        self.numchan            = numchan                           # Number of non-EOG electrodes
        self.ff_window          = ff_window                         # Fundamental freq. for HSD windowing
        self.h1_window          = h1_window                         # 1st harmonic freq. for HSD windowing
        self.fs                 = fs                                # Sampling rate of EEG
        self.mtp_npi            = mtp_npi                           # dimensionless width of the spectral averaging window
        self.mtp_nwin           = mtp_nwin                          # maximum number of tapers to combine
        self.psd_method         = psd_method
        self.n_stimuli          = len(self.stimHz)                  # how many stims on the screen needed to decode over
        self.nfft               = self.nextpow2(fs*dur)             # FFT next power of 2 length (buffer_length in secs)
        self.n_samples          = int(fs*dur)                       # Number of buffered length samples (1024 if 4s)
        self.freqspace          = fs/2*np.linspace(0,1,self.nfft/2+1) # Frequency space in Hz rather that sample number
        self.freqspace_windows  = self.freqSpaceWindows()           # Used to get HSD output
        self.use_baseline       = False                             # If no baseline was used the default is False
        if len(file_baseline) > 0:
            self.hsd_baseline   = np.genfromtxt(file_baseline)      # The HSD PSD baseline file for baseline removal
            self.use_baseline   = True                              # If baseline trial was ran, sets to True

    def nextpow2(self,i):
        n = 2
        while n < i: n *= 2
        return n

    def freqSpaceWindows(self):
        """ Selects values from a small window around each stimulating frequency in PSD space.
            Note that this is hard-wired to ONLY work with fundamental and first harmonic!
        """
        freqspace_windows = np.zeros((self.n_stimuli,2,2)) # freqspace_windows creates a 3D matrix!
        for stim in range(self.n_stimuli):
            # get the frequency window in Hz terms
            temp_hz_window  = [[self.stimHz[stim]-self.ff_window,self.stimHz[stim]+self.ff_window],
                               [2*self.stimHz[stim]-self.h1_window,2*self.stimHz[stim]+self.h1_window]]
            # now get the actual frequency samples in freqspace
            temp_freqspace_window = np.zeros((2,2))
            for i in range(0,2):
                for j in range(0,2):
                    temp_psd_window = abs(self.freqspace-temp_hz_window[i][j])
                    temp_psd_window = np.where(temp_psd_window==min(temp_psd_window))
                    temp_freqspace_window[i][j] = int(temp_psd_window[0])
            freqspace_windows[stim,:,:] = temp_freqspace_window
        return freqspace_windows

    def preproc(self,buffer_input):
        """ Preprocess the raw data input before running feature extraction methods.
        """
        y = np.zeros((self.numchan,buffer_input.shape[1]))
        for i in range(self.numchan):
            y[i,:] = buffer_input[i,:] - np.mean(buffer_input[i,:]) # Zero-mean raw data

        return y

    def multiTaper(self,y):
        """ Get the Multi-taper PSD for each electrode from EEG data.
            Note that npi is a float value, and nwin is an integer value.
        """
        mtp = np.zeros((self.numchan,y.shape[1]/2+1))
        for i in range(self.numchan):
            r        = pymutt.mtft(y[i,:], dt=1/self.fs, npi=self.mtp_npi, nwin=self.mtp_nwin)
            mtp[i,:] = r['power']
        self.f = np.arange(r['nspec']) * r['df'] # used for plotting only

        return mtp

    def fftSegment(self,y,fft_scale='mag'):
        """ Get the FFT PSD for each electrode from EEG data. fft_scale: 'mag' or 'db' options
        """
        yy = np.zeros((self.numchan,self.nfft))
        for i in range(self.numchan):
            if fft_scale == 'mag':
                yy[i,:] = abs(np.fft.fft(y[i,:],self.nfft))
            elif fft_scale == 'db':
                yy[i,:] = 20*np.log10(abs(np.fft.fft(y[i,:],self.nfft)))

        return yy

    def baselineCorrection(self,psd_data):
        """ Account for noise in the power spectrum for either FFT or MTP methods. """
        psd_corrected = psd_data - self.hsd_baseline

        return psd_corrected

    def harmonicSumDecision(self,y,psd_method='mtp'):
        """ Harmonic_mean_ff (and h1) look at PSD values over the mean of the window. This
            is done for all electrodes. Chose the mean axis wisely!! These two values are then summed. Lastly,
            the max value of the n stimulus directions is chosen as the winner. Ta da."""

        # Get the power spectrum
        if psd_method == 'fft':
            psd_data = self.fftSegment(y)                # FFT method
        elif psd_method == 'mtp':
            psd_data = self.multiTaper(y) # Multi-taper method

        # Remove the power spectrum baseline
        if self.use_baseline:
            psd_corrected = self.baselineCorrection(psd_data)
        else:
            psd_corrected = psd_data

        # Get the harmonic windows
        all_harmonic_sums = np.zeros(self.n_stimuli)
        for i in range(self.n_stimuli):
            single_freqspace_window = self.freqspace_windows[i,:,:]
            harmonic_mean_ff = np.mean(psd_corrected[:,single_freqspace_window[0][0]:single_freqspace_window[0][1]+1],axis=1)
            harmonic_mean_h1 = np.mean(psd_corrected[:,single_freqspace_window[1][0]:single_freqspace_window[1][1]+1],axis=1)
            all_harmonic_sums[i] = np.mean(harmonic_mean_ff+harmonic_mean_h1)

        # Pick a winner!
        self.hsd_winner = d = all_harmonic_sums.argmax()   # add "+1" if decision output is 1-4 (rather than 0-3)
        print "HSD: %d (%.1f Hz)" % (d+1, self.stimHz[d]), all_harmonic_sums / np.max(all_harmonic_sums)
    # def mtpPlot(self,mtp,plot_type="mtp_mean",x_min=10.0,x_max=17.0,plot_title=''):
    #     if plot_type == "mtp_all":
    #         y_min = min(mtp[2,np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         y_max = max(mtp[2,np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         plt.plot(self.f, np.transpose(mtp))
    #     elif plot_type == "mtp_mean":
    #         mtp_trial_mean = np.mean(mtp,axis=0)
    #         y_min = min(mtp_trial_mean[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         y_max = max(mtp_trial_mean[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         plt.plot(self.f,mtp_trial_mean)
    #     elif plot_type == "mtp_median":
    #         mtp_trial_median = np.median(mtp,axis=0)
    #         y_min = min(mtp_trial_median[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         y_max = max(mtp_trial_median[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         plt.plot(self.f,mtp_trial_median)
    #     elif plot_type == 'mtp_both':
    #         mtp_trial_mean = np.mean(mtp,axis=0)
    #         mtp_trial_median = np.median(mtp,axis=0)
    #         y_min = min(mtp_trial_mean[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         y_max = max(mtp_trial_mean[np.where(self.f==x_min)[0][0]:np.where(self.f==x_max)[0][0]])
    #         plt.plot(self.f,mtp_trial_mean)
    #         plt.plot(self.f,mtp_trial_median)
    #         plt.legend(['Multitaper Mean','Multitaper Median'])
    #     plt.xlim([10,17])
    #     plt.ylim([y_min,y_max])
    #     plt.title(plot_title)
    #     plt.show()

    def run(self,buffer_input):
        y = self.preproc(buffer_input)                            # preprocess buffered sample segment
        self.harmonicSumDecision(y, psd_method=self.psd_method)   # HSD on either FFT or MTP
        return self.hsd_winner