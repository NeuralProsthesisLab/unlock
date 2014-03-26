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
from __future__ import division
from optparse import OptionParser
from unlock.util import Trigger
import matplotlib.pyplot as plt
from unlock.analysis.accessor import NumpyDataTable
import numpy as np
import os

class Analyzer(object):
    def __init__(self, schema, data, write_to_file=False):
        super(Analyzer, self).__init__()
        self.schema = schema
        self.data = data
        self.write_to_file = write_to_file
        self.file_name = None

    def analyze(self):
        '''Subclass hook'''
        pass


class PlotAnalyzer(Analyzer):
    def __init__(self, schema, data, x_label, y_label, bar_label=None, title=None):
        super(PlotAnalyzer, self).__init__(schema, data)
        self.x_label = x_label
        self.y_label = y_label
        self.bar_label = bar_label
        self.title = title
        self.plot_title = None

    def make_plot(self, file_name):
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title+'-'+str(self.plot_title))
        if self.bar_label:
            plt.colorbar().set_label(self.bar_label)

        if file_name:
            plt.savefig(file_name)
        else:
            plt.show()

    def analyze(self):
        pass


class FrequencyPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, data, x_label='Frequency (Hz)', y_label='Power (dB)', title='Frequency plot'):
        super(FrequencyPlotAnalyzer, self).__init__(schema, data, x_label, y_label, title=title)

    def analyze(self):
        try:
            #from numpy import sin, linspace, pi
            #from pylab import plot, show, title, xlabel, ylabel, subplot
            import scipy
            import pylab
            #from scipy import fft, arange
            y = np.hstack(self.data.signal_data(self.slice))

            # def plotSpectrum(y, Fs):
            #     n = len(y)  # length of the signal
            #     k = np.arange(n)
            #     T = n / Fs
            #     frq = k / T  # two sides frequency range
            #     #import pdb
            #     #pdb.set_trace()
            #     frq = frq[:int(n / 2)]  # one side frequency range
            #
            #     Y = scipy.fft(y) / n  # fft computing and normalization
            #     Y = Y[:int(n / 2)]
            #
            #     pylab.plot(frq, abs(Y), 'r')  # plotting the spectrum
            #     pylab.xlabel('Freq (Hz)')
            #     pylab.ylabel('|Y(freq)|')
            #
            # Fs = 256  # sampling rate
            # Ts = 1.0 / Fs  # sampling interval
            # t = np.arange(0, self.data.signal_rows()/self.schema.sampling_rate_hz, Ts)  # time vector
            #
            # ff = 5  # frequency of the signal
            # #y = np.sin(2*np.pi*ff*t)
            #
            #
            # pylab.subplot(2, 1, 1)
            # print("t shape = ", t.shape)
            # import pdb
            # #pdb.set_trace()
            # print("y shape = ", y.shape)
            # pylab.plot(t, y)
            # pylab.xlabel('Time')
            # pylab.ylabel('Amplitude')
            # pylab.subplot(2, 1, 2)
            # plotSpectrum(y, Fs)
            # pylab.show()
        except:
            pass

        #return
        import time

        print('signal shape =', y.shape)
        #time.sleep(1)
        #print("signal = ", signal)
        #print("signal.transpose = ", signal.transpose())
        # plt.clf()
        # fft = np.fft.fft(y)
        # time_step = 1/256
        # freq = np.fft.fftfreq(y.size, time_step)
        # power = np.abs(fft)**2
        # plt.plot(freq, power)
        # self.make_plot(self.file_name)
        #
        plt.subplot(2, 1, 1)
        ts = 1.0 / self.schema.sampling_rate_hz
        t = np.arange(0, self.data.signal_rows()/self.schema.sampling_rate_hz, ts)  # time vector
        plt.plot(t, y)
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.subplot(2, 1, 2)
        plt.clf()
        ps = np.abs(np.fft.fft(y))**2
        time_step = 1 / 256
        freqs = np.fft.fftfreq(y.size, time_step)
        idx = np.argsort(freqs)
        print('idx = ', idx)
        plt.plot(freqs[idx], ps[idx])
        self.make_plot(self.file_name)

class SpectrogramPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, data, x_label='Time (s)', y_label='Frequency (Hz)', bar_label='Amplitude (Frequency power)',
                 title='Spectrogram'):
        super(SpectrogramPlotAnalyzer, self).__init__(schema, data, x_label, y_label, bar_label, title)
        self.slice = None

    def analyze(self):
        plt.clf()
        data = filter_low_high_pass(np.hstack(self.data.signal_data(self.slice)))
        plt.specgram(data, NFFT=256, Fs=self.schema.sampling_rate_hz)
        self.make_plot(self.file_name)


class MultiPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, analyzers=[], data_loader=None, output_prefix=None):
        super(MultiPlotAnalyzer, self).__init__(schema, None, None, None)
        self.analyzers = analyzers
        self.data_loader = data_loader
        self.path_prefix = os.path.join(*output_prefix)
        for analyzer in self.analyzers:
            analyzer.schema = schema

    def analyze(self):
        for data_loader in self.data_loader.file_generator():
            results_directory = os.path.join(self.path_prefix, data_loader.directory)
            os.makedirs(results_directory, exist_ok=True)
            for instance in self.analyzers:
                for data_channel_slice in self.schema.single_channel_generator():
                    instance.slice = data_channel_slice
                    instance.data = NumpyDataTable(self.schema, data_loader.load())
                    instance.plot_title = data_loader.directory + data_loader.file_name+str(data_channel_slice)
                    #instance.file_name = os.path.join(results_directory, instance.title+data_loader.file_name+str(data_channel_slice)+'.plot.png')
                    print("Title =", instance.title, "slice = ", data_channel_slice, " data channels = ", self.schema.data_channels())
                    #print("File name is = ", instance.file_name)
                    instance.analyze()

def filter_low_high_pass(signal_data, low_filter=2, high_filter=80, Fs=1/256):
    #ls = range(len(data)) # data contains the function
    freq = np.fft.fftfreq(signal_data.size, d = 256)
    fft = np.fft.fft(signal_data)
    x = freq[:len(signal_data)/2]
    print ("size, data = ", x.size, np.hstack(x)*256)
    import sys
    sys.exit(0)
    for i in range(len(x)):
        print ("X[i] = ", x[i])
        if x[i] > high_filter: # cut off all frequencies higher than 0.005
            fft[i] = 0.0
            fft[len(signal_data)/2 + i] = 0.0
        elif x[i] < 2:
            fft[i] = 0
            fft[len(signal_data)/2 + i] = 0.0
    inverse = np.fft.ifft(fft)
    return inverse
