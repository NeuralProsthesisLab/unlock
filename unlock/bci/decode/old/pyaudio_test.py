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

# change audio to be 2 channels and lowest sample frequence 
class EMG:
	def __init__(self,numChans=2,sampleRate=11025,chunkSize=512,rmsWindows=5):
		self.sampleRate = sampleRate
		self.chunkSize = chunkSize 
		self.numChans = numChans
		self.rmsWindows = rmsWindows
		self.p = pyaudio.PyAudio()
		
		self.theStream = self.p.open(format=pyaudio.paInt16,
									 channels = self.numChans,
									 rate = self.sampleRate,
									 input = True,
									 frames_per_buffer = self.chunkSize,
									 start = False)
									# input_device_index=useDevice)
		
		# create the containers to store the acquired data
		# using deque because it's supposedly fast and can implement a circular
		# buffer efficiently
		self.rawData = collections.deque([])
		self.rmsBuffer = collections.deque([],maxlen=rmsWindows)
		self.timeStamp = collections.deque([])
		
		# other definitions:
		# to convert the wave stream data into an array 
		self.convertSamplesFormat = ('%ih' % (self.rmsWindows*self.chunkSize*
											  self.numChans) )
		
	### handle the sound card and pyAudio stuff
	#### start_recording and stop_recording are just acting as a switch
	def start_recording(self):
		# start the stream
		print ('recording started')
		self.theStream.start_stream()
		# fill self.rmsBuffer with some bullshit for now
		print ('stream started')
		self.file_handle = open("%s_%d.txt" % ('pyaudio-test', time.time()), 'wb')
		for q in range(5):
			dataIn = self.theStream.read(self.chunkSize)
			udata = np.array(struct.unpack('<%dh' % (self.chunkSize*self.numChans), dataIn)).reshape(self.chunkSize, self.numChans)
			np.savetxt(self.file_handle, udata, fmt='%d', delimiter='\t')

		self.file_handle.close()
		
if __name__ == '__main__':
	emg = EMG()
	emg.start_recording()