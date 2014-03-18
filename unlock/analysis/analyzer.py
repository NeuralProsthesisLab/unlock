# Copyright (c) James Percent and Unlock contributors.
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

from optparse import OptionParser
from unlock.util import Trigger
import matplotlib.pyplot as plt
import numpy as np
import sys

class Analyzer(object):
    def __init__(self, schema, data):
        super(Analyzer, self).__init__()
        self.schema = schema
        self.data = data

    def analyze(self):
        '''Subclass hook'''
        pass

class PlotAnalyzer(Analyzer):
    def __init__(self, schema, data, x_label, y_label, bar_label=None):
        super(PlotAnalyzer, self).__init__(schema, data)
        self.x_label = x_label
        self.y_label = y_label
        self.bar_label = bar_label

    def make_plot(self, file_name):
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        if self.bar_label:
            plt.colorbar().set_label(self.bar_label)

        if file_name:
            plt.savefig(file_name)
        else:
            plt.show()

    def analyze(self, file_name):
        super(PlotAnalyzer, self).analyze(file_name)


class FrequencyPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema=None, data=None, x_label='Frequency (Hz)', y_label='Power (dB)'):
        super(FrequencyPlotAnalyzer, self).__init__(schema, data, x_label, y_label)
        assert schema and data

    def analyze(self, file_name=None):
        self.data.load()
        signal = self.data.signal_data()
        print("signal = ", signal)
        print("signal.transpose = ", signal.transpose())
        fft = np.fft.fft(signal)
        timestep = 256

        freq = np.fft.fftfreq(signal.size, timestep)
        power = 10*np.log10(np.abs(fft)**2)
        plt.plot(freq, power)
        self.make_plot(file_name)


class SpectrogramPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema=None, data=None, x_label='Time (s)', y_label='Frequency (Hz)', bar_label='Amplitude (Frequency power)'):
        super(SpectrogramPlotAnalyzer, self).__init__(schema, data, y_label, x_label, bar_label)
        assert schema and data

    def analyze(self, file_name=None):
        time,signal = [],[]
        self.data.load()
        plt.specgram(self.data.signal_data(), NFFT=256, Fs=self.schema.sampling_rate_hz)
        self.make_plot(file_name)


