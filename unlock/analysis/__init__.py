# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.import socket

from unlock.util import AbstractFactory
from unlock import UnlockFactory
from unlock.analysis.accessor import *
from unlock.analysis.analyzer import *
from unlock.analysis.filter import *
import os


class AnalysisFactory(UnlockFactory):
    def __init__(self):
        super(AnalysisFactory, self).__init__()

    def mobilab_milli_volts_transformer(self, channel_sensitivity=500):
        return MobilabMilliVoltsDataTransformer(channel_sensitivity)

    def schema_with_timestamps_and_cues(self,
        data={'o1':0, 'oz':1, 'o2':3, 'po3':4, 'poz': 5, 'po4': 6, 'cz':7, 'fcz':8},
        timestamps={'c++': 9, 'python': 10},
        triggers={'sequence_trigger': 11, 'sequence_trigger_time_stamp': 12, 'cue_trigger': 13, 'cue_trigger_time_stamp': 14},
        sampling_rate_hz=256, start=None, end=None):

        schema = Schema(data, timestamps, triggers, sampling_rate_hz, start, end)
        return schema

    def numpy_data_table(self, schema=None, loader=None):
        return NumpyDataTable(schema, loader.load())

    def spectrogram(self, schema=None, data_table=None):
        return SpectrogramPlotAnalyzer(schema, data_table)

    def butterworth_bandpass_filter(self, schema=None, low_cutoff=4, high_cutoff=65):
        return Butterworth(schema.sampling_rate_hz, low_cutoff, high_cutoff)

    def numpy_file_system_data_loader(self, file_path=['data', 'mobilab-3-14', 'ssvep-diag-12z-mobilab-frame_count-vsync_1394832864.txt'],
                                      separator='\t', transformer=DataTransformer()):
        file_path = os.path.join(*file_path)
        return NumpyFileSystemDataLoader(file_path, separator, transformer)

    def frequency_plot(self, schema=None, data_table=None):
        return FrequencyPlotAnalyzer(schema, data_table)

    def multi_plot_analyzer(self, analyzers=None, schema=None, data_loader=None, output_prefix=None, filter=None):
        return MultiPlotAnalyzer(schema, analyzers, data_loader, output_prefix, filter)

    def directory_scanner(self, directory=os.path.join(['data', 'mobilab-3-14']), file_filter=r'.*\.txt', transformer=None):
        assert directory and file_filter and transformer
        return DirectoryScanner(directory, file_filter, transformer)

