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
import matplotlib.pyplot as plt
from unlock.analysis.accessor import NumpyDataTable
from unlock.analysis.filter import Filter
import numpy as np
import os


class Analyzer(object):
    def __init__(self, schema, data, filter=None, write_to_file=False):
        super(Analyzer, self).__init__()
        self.schema = schema
        self.data = data
        self.write_to_file = write_to_file
        self.file_name = None
        if not filter:
            self.filter = lambda x: x

    def analyze(self):
        '''Subclass hook'''
        pass


class PlotAnalyzer(Analyzer):
    def __init__(self, schema, data, x_label, y_label, bar_label=None, title=None, filter=None):
        super(PlotAnalyzer, self).__init__(schema, data, filter=filter)
        self.x_label = x_label
        self.y_label = y_label
        self.bar_label = bar_label
        self.title = title
        self.plot_title = None

    def make_plot(self, file_name):
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)

        if self.bar_label:
            plt.colorbar().set_label(self.bar_label)

        if file_name:
            plt.savefig(file_name)
        else:
            plt.show()

    def prepare_numpy_matrix(self):
        plt.clf()
        #data = self.filter.apply(np.hstack(self.data.signal_data(self.slice)))
        print("signal data: ",self.data.signal_data(self.slice))
        data = np.hstack(self.data.signal_data(self.slice))
        return data

    def analyze(self):
        pass


class FrequencyPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, data, x_label='Frequency (Hz)', y_label='Power (dB)', title='Frequency plot'):
        super(FrequencyPlotAnalyzer, self).__init__(schema, data, x_label, y_label, title=title, filter=None)

    def analyze(self):
        data = self.prepare_numpy_matrix()

        plt.subplot(2, 1, 1)
        ts = 1.0 / self.schema.sampling_rate_hz
        t = np.arange(0, self.data.signal_rows()/self.schema.sampling_rate_hz, ts)  # time vector
        plt.plot(t, data)
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.subplot(2, 1, 2)
        ps = np.abs(np.fft.fft(data))**2
        time_step = 1 / 256
        freqs = np.fft.fftfreq(data.size, time_step)
        idx = np.argsort(freqs)
        ps_values = ps[idx]
        freq_values = freqs[idx]
        filtered = [[],[]]
        assert len(freq_values) == len(ps_values)
        # XXX - this is a hack
        for i in range(len(freq_values)):
            if freq_values[i] < 20 and freq_values[i] > -20:
                filtered[0].append(freq_values[i])
                filtered[1].append(ps_values[i])
        plt.plot(filtered[0], filtered[1])
        self.make_plot(self.file_name)


class SpectrogramPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, data, nfft=3, x_label='Time (s)', y_label='Frequency (Hz)', bar_label='Amplitude (Frequency power)',
                 title='Spectrogram', filter=None):
        super(SpectrogramPlotAnalyzer, self).__init__(schema, data, x_label, y_label, bar_label, title)
        #self.slice = schema.data_channels()
        #print("the data channel rows are", schema.data_channels())
        self.nfft = 3

    def analyze(self):
        data = self.prepare_numpy_matrix()# np.hstack(self.data.signal_data(self.slice)) #filter_low_high_pass(np.hstack(self.data.signal_data(self.slice)))
        plt.specgram(data, NFFT=self.nfft*self.schema.sampling_rate_hz, Fs=self.schema.sampling_rate_hz)
        plt.axis([0,3,0,35])
        self.make_plot(self.file_name)


class MultiPlotAnalyzer(PlotAnalyzer):
    def __init__(self, schema, analyzers=[], data_loader=None, output_prefix=None, filter=None):
        super(MultiPlotAnalyzer, self).__init__(schema, None, None, None, filter=filter)
        self.analyzers = analyzers
        self.data_loader = data_loader
        self.path_prefix = os.path.join(*output_prefix)
        for analyzer in self.analyzers:
            analyzer.schema = schema
            analyzer.filter = filter

    def analyze(self):
        for data_loader in self.data_loader.file_generator():
            results_directory = os.path.join(self.path_prefix, data_loader.directory)
            os.makedirs(results_directory, exist_ok=True)
            for data_channel_slice in self.schema.single_channel_generator():
                for instance in self.analyzers:
                    instance.slice = data_channel_slice
                    instance.data = NumpyDataTable(self.schema, data_loader.load())
                    instance.plot_title = data_loader.directory + data_loader.file_name+str(data_channel_slice)
                    instance.file_name = os.path.join(results_directory, data_loader.file_name+'-'+instance.title+'-'+self.schema.get_channel_name(data_channel_slice)+'.png')
                    instance.analyze()

