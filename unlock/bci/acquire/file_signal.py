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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import numpy as np
import threading
import collections
import struct
import time

import numpy as np
import logging
import time
import math

class MemoryResidentFileSignal(object):
	def __init__(self, filename, timer, channels=4, sampling_hz=256, delimiter='\t', dtype=np.int32):
		super(MemoryResidentFileSignal, self).__init__()
		self.logger = logging.getLogger(__name__)
		self.filename = filename
		self.file = None
		self.data = None
		self.cursor = 0
		self.timer = timer
		self.sampling_hz = sampling_hz
		self.samples_per_milli_sec = self.sampling_hz / 1000.0
		self.chans = channels
		self.delimiter = delimiter
		self.dtype = dtype
		
	def open(self, macaddr):
		return True
			
	def init(self, channels):
		self.chans = channels
		return True
		
	def channels(self):
		return self.chans
		
	def start(self):
		assert self.file is None
		self.file = open(self.filename, 'r')
		self.data = np.loadtxt(self.file, delimiter=self.delimiter, dtype=self.dtype)
		self.last = self.timer.elapsedMilliSecs()
		assert len(self.data.shape) == 2 and self.data.shape[1] == self.chans
		self.cursor = 0
		return True
		
	def acquire(self):
		milli_secs  = (self.timer.elapsedMilliSecs() - self.last)
		samples = math.floor(milli_secs * self.samples_per_milli_sec)
		self.last = self.timer.elapsedMilliSecs()
		return samples
		
	def getdata(self, samples):
		next_slice = self.data[self.cursor:self.cursor+samples]
		self.cursor += samples
		return next_slice
	
	def getEaplsedMicros(self):
		return self.timer.elapsedMicroSecs()
		
	def timestamp(self):
		return self.timer.elapsedMicroSecs()
		
	def stop(self):
		assert self.file is not None
		self.file.close()
		self.file = None
		self.data = None
		return True
		
	def close(self):
		return True			
		
if __name__ == '__main__':
	from neuralsignal import *
	timer = create_timer()
	f = MemoryResidentFileSignal('../../analysis/data/valid/emg_signal_1380649383_tongue_c.5_r.5_i1.txt', timer, channels=17)
	f.start()
	import time
	time.sleep(1)
	while True:
		samples = f.acquire()
		print('samples = ', samples)
		print('shape of data =' , f.getdata(samples).shape)
		time.sleep(1)
	