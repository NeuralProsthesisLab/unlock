# Copyright (c) Byron Galbraith and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np
import scipy.signal as sig
from unlock.model.model import UnlockModel


class TimeScopeState(UnlockModel):
    def __init__(self, n_channels=1, fs=256, duration=2):
        super(TimeScopeState, self).__init__()
        self.n_channels = n_channels
        self.fs = fs
        self.duration = duration
        self.n_samples = self.duration * self.fs

        self.cursor = 0
        self.traces = np.zeros((self.n_samples, self.n_channels))
        self.yscale = 1
        self.yshift = np.zeros(self.n_channels)

        self.refresh_rate = 1/20.0
        self.elapsed = 0
        self.state_change = False

    def get_state(self):
        update = self.state_change
        if self.state_change:
            self.state_change = False
        return update, self.cursor, self.traces, self.yshift, self.yscale

    def process_command(self, command):
        if command.delta is not None:
            self.elapsed += command.delta
            if self.elapsed >= self.refresh_rate:
                self.state_change = True
                self.elapsed = 0

        if not command.is_valid():
            return

        samples = command.matrix[:, 0:self.n_channels]
        s = samples.shape[0]
        idx = np.arange(self.cursor, self.cursor+s) % self.n_samples
        self.traces[idx] = samples
        last_cursor = self.cursor
        self.cursor += s
        self.cursor %= self.n_samples

        # compute auto-scaling parameters
        if self.cursor < last_cursor:
            max = np.max(self.traces)
            scale = np.round(0.5*(max - np.min(self.traces)), 2)
            shift = np.max(self.traces, axis=0) - scale
            if scale != 0:
                #if 0.9*self.yscale < 100.0 / scale < 1.1*self.yscale:
                #    pass
                #else:
                self.yscale = 100.0 / scale
                #if 0.9*self.yshift < shift < 1.1*self.yshift:
                #    pass
                #else:
                self.yshift = shift


class FrequencyScopeState(UnlockModel):
    def __init__(self, n_channels=1, fs=256, duration=2, nfft=None,
                 freq_range=None, display_channels=None):
        super(FrequencyScopeState, self).__init__()

        self.n_channels = n_channels
        self.fs = fs
        self.duration = duration
        self.nfft = nfft
        self.n_samples = self.duration * self.fs
        self.data = np.zeros((self.n_samples, self.n_channels))

        if self.nfft is None:
            self.nfft = self.n_samples
        self.fft_bin_width = fs / self.nfft
        self.fft_bins = self.fft_bin_width*np.arange(self.nfft/2 + 1)

        if freq_range is None:
            freq_range = (0, fs/2)
        assert freq_range[0] >= 0, freq_range[1] <= fs / 2

        self.freq_begin = freq_range[0]
        self.freq_end = freq_range[1]
        self.trace_begin = np.floor(self.freq_begin / self.fft_bin_width)
        self.trace_end = np.ceil(self.freq_end / self.fft_bin_width) + 1
        self.trace = np.zeros(self.trace_end - self.trace_begin)

        self.display_channels = display_channels
        if display_channels is None:
            self.display_channels = [0]
        self.refresh_rate = 1/20.0
        self.elapsed = 0
        self.state_change = False

        #self.test_signal = np.zeros(self.data.shape)
        #for i in range(self.n_channels):
        #    self.test_signal[:,i] = 300000000*np.sin((12+i)*2*np.pi*np.arange(0, self.duration, 1/self.fs))

    def get_state(self):
        update = self.state_change
        if self.state_change:
            self.state_change = False
        return update, self.trace

    def process_command(self, command):
        if command.delta is not None:
            self.elapsed += command.delta
            if self.elapsed >= self.refresh_rate:
                self.state_change = True
                self.elapsed = 0

        if not command.is_valid():
            return

        samples = command.matrix[:, 0:self.n_channels]
        s = samples.shape[0]
        self.data = np.roll(self.data, -s, axis=0)
        #self.test_signal = np.roll(self.test_signal, -s, axis=0)
        self.data[-s:] = samples  #+ self.test_signal[-s:]
        _, psd = sig.periodogram(self.data[:, self.display_channels],
                                 fs=self.fs, nfft=self.nfft, axis=0)
        #fft = np.abs(np.fft.rfft(self.data[:, [0]], n=self.nfft, axis=0))
        self.trace = psd[self.trace_begin:self.trace_end]
        self.trace /= np.max(self.trace)

    def change_display_channel(self, change):
        if len(self.display_channels) > 1:
            return

        new_chan = self.display_channels[0] + change
        if new_chan >= self.n_channels:
            new_chan = self.n_channels - 1
        elif new_chan < 0:
            new_chan = 0
        self.display_channels[0] = new_chan