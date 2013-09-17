import numpy as np
import scipy.signal as sig

class MSequenceTemplateMatcher():
    """
    m-sequence template matching builds up templates from stereotyped EEG
    response in the time domain then scores actual trial data against the
    templates.

    this approach requires a training phase, which can be triggered by the lack
    of a provided trained classifier or a recalibration at decoder
    initialization.

    """
    def __init__(self, nTargets, bits, fd, fs, electrodes):
        self.nTargets = nTargets
        self.fs = fs
        # self.nSamples = int(duration * fs)
        self.overflow = 16
        self.buffer = np.zeros((self.nSamples + self.overflow, electrodes))
        self.cursor = 0

        # template time = sequence length / display freq e.g. 31bits / 30hz = ~1s
        # template legth = template time * fs e.g. 1s * 256hz = 256 samples
        self.templates = np.zeros(((bits / fd) * fs, nTargets))
        self.isTraining = True


    def train(self):
        """
        build the templates from initial cued training session
        """
        pass




    def process(self, samples):
        """
        samples assumes an ndarray of shape (samples, electrodes)
        train vs test


        If we fill the buffer, perform the analysis.
        """
        s = samples.shape[0]
        self.buffer[self.cursor:self.cursor+s,:] = samples
        self.cursor += s

        if self.cursor >= self.nSamples:
            #self.hsd.run((self.buffer[0:self.nSamples,1:4] - self.buffer[0:self.nSamples,6].reshape((self.nSamples,1))).T)
            x = self.buffer[0:self.nSamples,1:4] - self.buffer[0:self.nSamples,6].reshape((self.nSamples,1))
            #x = sig.detrend(x,axis=0)
            #x = sig.detrend(self.buffer[0:self.nSamples],axis=0)
            #x = x[:, 1:4]# - x[:,5:8]# - \
            #self.buffer[0:self.nSamples, 5:8]
            x -= np.mean(x, axis=0)
            x = np.abs(np.fft.rfft(self.window * x, n=self.nfft, axis=0))
            sums = np.zeros(len(self.targets))
            for i in xrange(len(self.targets)):
                sums[i] = np.sum(x[self.harmonics[i],:])
            d = np.argmax(sums)
            np.set_printoptions(precision=2)
            print "HSD: %d (%.1f Hz)" % (d+1, self.targets[d]), sums / np.max(sums)
            d = -1
            self.cursor = 0
            return d
