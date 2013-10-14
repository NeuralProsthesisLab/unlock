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
import pyaudio
import time

class AudioSignal(object):
	def __init__(self,channels=2,sampling_rate=22050,batch_size=512,window_size=5):
		super(AudioSignal, self).__init__()
		self.sampling_rate = sampling_rate
		self.batch_size = batch_size 
		self.chans = channels
		self.window_size = window_size
		self.py_audio = pyaudio.PyAudio()
		self.audio_stream_buffer = collections.deque([],maxlen=window_size)
		
	def start_recording(self):
		# start the stream
		print ('recording started')
		self.audio_stream.start_stream()
		# fill self.audio_stream_buffer with some bullshit for now
		print ('stream started')
		self.file_handle = open("%s_%d.txt" % ('pyaudio-test', time.time()), 'wb')
		for q in range(5):
			dataIn = self.audio_stream.read(self.batch_size)
			udata = np.array(struct.unpack('<%dh' % (self.batch_size*self.chans), dataIn)).reshape(self.batch_size, self.chans)
			np.savetxt(self.file_handle, udata, fmt='%d', delimiter='\t')
			
		self.file_handle.close()
			
	def open(self, macaddr):
		self.mac = macaddr
		return True
			
	def init(self, channels):
		self.chans = channels
		return True
		
	def channels(self):
		return self.chans
		
	def start(self):
		self.audio_stream = self.py_audio.open(format=pyaudio.paInt16,
									 channels = self.chans,
									 rate = self.sampling_rate,
									 input = True,
									 frames_per_buffer = self.batch_size,
									 start = False)		
		self.audio_stream.start_stream()
		return True
		
	def acquire(self):
		audio_data = self.audio_stream.read(self.batch_size)
		self.next_sample_batch = struct.unpack('<%dh' % (self.batch_size*self.chans), audio_data)#).reshape(self.batch_size, self.channels)
		#print(type(self.next_sample_batch))
		assert self.batch_size*self.chans == len(self.next_sample_batch)
		return len(self.next_sample_batch)
		
	def getdata(self, samples):
		#print("size of samples = ", samples)
		assert samples == len(self.next_sample_batch)
		return self.next_sample_batch
		
	def getEaplsedMicros(self):
		pass
		
	def timestamp(self):
		pass
		
	def stop(self):
		pass
		
	def close(self):	
		self.audio_stream.close()
		
		
if __name__ == '__main__':
	emg = AudioSignal()
	emg.start_recording()