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

import numpy as np

__author__ = 'jpercent'

class DataTransformer(object):
    def apply(self, datum):
        return datum

class MobilabMilliVoltsDataTransformer(DataTransformer):
    def __init__(self, channel_sensitivity=500):
        self.channel_sensitivity = channel_sensitivity
        self.resolution_factor = (10 /2**18) * self.channel_sensitivity
        self.micro_to_millis_factor = 1000

    def apply(self, datum):
        return datum * self.resolution_factor * self.micro_to_millis_factor


class PersistentDataTransformer(DataTransformer):
    def __init__(self, transformer, file_name, row_size):
        self.transformer = transformer
        self.file_name = file_name
        self.file_open = False
        self.file_desc = None
        self.row = np.zero(row_size)
        self.row_size = row_size
        self.cursor = 0

    def open(self):
        self.file_open = True
        self.file_desc = open(self.file_name, 'w+')

    def close(self):
        self.file_open = False
        self.file_desc.close()

    def apply(self, datum):
        assert self.file_open and self.file_desc
        transformed_datum = self.transformer.apply(datum)
        self.row[self.cursor] = datum
        self.cursor += 1
        if self.cursor == self.row_size:
            self.row.tofile(self.file_desc, sep='\t', format='%s')
            cursor = 0

        return transformed_datum


class DataLoader(object):
    def __init__(self):
        super(DataLoader, self).__init__()
    def load(self):
        return []
    def store(self, data, file_name):
        pass


class NumpyFileSystemDataLoader(object):
    def __init__(self, file_path, separator='\t', transformer=DataTransformer()):
        super(NumpyFileSystemDataLoader, self).__init__()
        self.file_path = file_path
        self.separator = separator
        self.transformer = transformer

    def load(self):
        np_array = np.array([[self.transformer.apply(float(datum)) for datum in line.split(self.separator)] for line in open(self.file_path)])
        #print ('shape = ', np_array.shape, " some rows = ", np_array[0:10, 0:8])
        return np_array

    def store(self, file_name, np_array):
        np.savetxt(file_name, np_array, fmt='%s', delimiter='\t')


class Schema(object):
    def __init__(self, data, timestamps, triggers, sampling_rate_hz):
        super(Schema, self).__init__()
        self.data_dict = data
        self.sample_timestamp_dict = timestamps
        self.trigger_dict = triggers
        self.sampling_rate_hz = sampling_rate_hz

    def data(self):
        return sorted([value for key, value in self.data_dict.items()])

    def data_channel_combinations_generator(self):
        values = self.data()
        # we compute the power set here, minus the empty set;  create a set with the first element.  loop through the
        #  rest of the elements and create a new set for itself and each existing subset.  Booyakasha.
        subsets = None
        for value in values:
            if not subsets:
                subsets = [value]
                yield subsets
            else:
                subsets.extend(value)
                new_subsets = [ value + subset for subset in subsets]
                yield new_subsets
                subsets.extend(new_subsets)

    def timestamps(self):
        return sorted([value for key,value in self.timestamp_dict.items()])

    def triggers(self):
        return sorted([value for key,value in self.trigger_dict.items()])


class NumpyDataTable(object):
    def __init__(self, schema, raw_data):
        super(NumpyDataTable, self).__init__()
        self.schema = schema
        self.raw_data = raw_data

    def signal_rows(self):
        rows = self.raw_data.shape[0]
        if rows % self.schema.sampling_rate_hz:
            rows = int(rows/self.schema.sampling_rate_hz)
        return rows

    def signal_data(self):
        assert self.data_loaded
        rows = self.signal_rows()
        columns = self.schema.data()
        return self.raw_data[ 256*rows: , columns]


class OtherMobilabInfo(DataTransformer):
    def __init__(self, sampling_hz=256, high_pass_filter_bound=0.5, low_pass_filter_bound=100):
        self.sampling_hz = sampling_hz
        self.high_pass = high_pass_filter_bound
        self.low_pass = low_pass_filter_bound

# notes from andres; he sent a follow up email that says the channel sensitivity should be 500 not 5/10 (as written below)
#
#                 Fs               = 256;                                % Sampling frequency
#chSensit      = 500/1000;                        % channel sensitivity is 500 microvolts, passing from micro to millivolts
#filtHigh          = 0.5;                                % high pass bound for filter
#filtLow           = 100;                               % low pass bound for filter
#resolutFactor = (2*5/(2^16*4))*(chSensit); % resolution factor to multiply raw data to get it in millivolts
#The data read by unlock is then multiplied by the resolution factor (resolutFactor):
#unlockData.data     = rawData*resolutFactor*1000;         % This gives data in milliVolts, how it is usually

#I dug deeper into the matter of the format of the recorded data to be output in millivolt values and realized I was
# dividing by an extra 1000 value in the formula. The channel sensitivity I gave you yesterday was 500/1000 but it
# should be in reality 500. This means the 1000 should be removed.