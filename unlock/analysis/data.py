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

class DataLoader(object):
    def __init__(self):
        super(DataLoader, self).__init__()

    def load(self):
        '''Subclass hook'''
        return []

    def store(self, data, file_name):
        '''Subclass hook'''

class NumpyFileSystemDataLoader(object):
    def __init__(self, file_path, separator='\t'):
        super(NumpyFileSystemDataLoader, self).__init__()
        self.file_path = file_path
        self.separator = separator

    def load(self):
        print ("NP load text ", self.file_path, self.separator)
        # python got all sexy on me
        size = None
        for line in open(self.file_path):
            if not size:
                size = len(line)
            #assert size == len(line)

        np_array = np.array([[float(datum) for datum in line.split(self.separator)] for line in open(self.file_path)])
        print ('sample = ', np_array.shape)
        return np_array

    def store(self, data, file_name):
        raise RuntimeError('Unsupported')

class Schema(object):
    def __init__(self, data, timestamps, triggers, sampling_rate_hz):
        super(Schema, self).__init__()
        self.data_dict = data
        self.sample_timestamp_dict = timestamps
        self.trigger_dict = triggers
        self.sampling_rate_hz = sampling_rate_hz

    def data(self):
        values = [ value for key, value in self.data_dict.items()]
        values.sort()
        print('values ', values)
        return values

    def timestamps(self):
        return self.timestamp_dict.values().sort()

    def triggers(self):
        return self.trigger_dict.values().sort()

class NumpyDataTable(DataLoader):
    def __init__(self, schema, loader):
        super(NumpyDataTable, self).__init__()
        self.schema = schema
        self.loader = loader
        self.data_loaded = False

    def load(self):
        self.raw_data = self.loader.load()
        assert len(self.raw_data.shape) == 2
        self.data_loaded = True

    def all_data(self):
        assert self.data_loaded
        return self.raw_data

    def raw_signal_data(self):
        assert self.data_loaded
        print("raw data = ", self.raw_data)

        ret = self.raw_data[slice(self.schema.data()), 12 ]
        print ('ret of 0 = ', ret[0])
        #print ("slice = ", ret)
        return ret

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

