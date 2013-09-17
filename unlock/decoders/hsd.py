import numpy as np
from unlock.model import UnlockModel
from unlock.controller import VEPCommand

class HarmonicSumDecision(UnlockModel):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, targets, duration, fs, electrodes, filters=None):
        super(HarmonicSumDecision, self).__init__()
        self.targets = targets
        self.target_window = 0.1
        self.fs = fs
        self.electrodes = electrodes
        self.nSamples = int(duration * fs)
        self.overflow = 16
        self.buffer = np.zeros((self.nSamples + self.overflow, electrodes))
        self.cursor = 0
        self.filters = filters

        self.fft_params()

    def fft_params(self):
        """Determine all the relevant parameters for fft analysis"""
        i = 2
        while i <= self.nSamples:
            i *= 2
        self.nfft = i
        self.window = 1 #np.hanning(self.nSamples).reshape((self.nSamples, 1))

        # indices for frequency components
        # as the values returned by the fft are in freq space, the resolution
        # is limited to the size of the fft, which in this case is just the
        # next largest power of 2. for a small time window, this results in
        # poor frequency resolution.
        self.nHarmonics = 2
        self.harmonics = []
        f = np.fft.fftfreq(self.nfft, 1.0/self.fs)[0:self.nfft/2]
        f_step = f[1]
        for target in self.targets:
            r = []
            for h in range(1, self.nHarmonics+1):
                q = h * target / f_step
                # q = np.where(np.logical_and(f > h*target - self.target_window,
                #                             f < h*target + self.target_window))
                r.extend([np.floor(q), np.ceil(q)])
            self.harmonics.append(r)

    def process_command(self, command):
        """
        command contains a data matrix of samples assumed to be an ndarray of
         shape (samples, electrodes+)

        command can also contain directives to reset the buffer
        """
        samples = command.matrix[:, 0:self.electrodes]
        s = samples.shape[0]
        self.buffer[self.cursor:self.cursor+s, :] = samples
        self.cursor += s

        if self.cursor >= self.nSamples:
            x = self.buffer[0:self.nSamples]
            if self.filters is not None:
                x = self.filters.apply(x)
            y = np.abs(np.fft.rfft(self.window * x, n=self.nfft, axis=0))
            sums = np.zeros(len(self.targets))
            for i in range(len(self.targets)):
                sums[i] = np.sum(y[self.harmonics[i], :])
            d = np.argmax(sums)
            np.set_printoptions(precision=2)
            print("HSD: %d (%.1f Hz)" % (d+1, self.targets[d]),
                sums / np.max(sums))
            ## TODO: roll any leftover samples to the beginning of the buffer
            self.cursor = 0
            command.decision = d + 1