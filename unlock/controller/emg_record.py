import numpy
import threading
import collections
import struct
import pyaudio
import time

class EMG:
	def __init__(self,numChans=2,sampleRate=44100,chunkSize=512,rmsWindows=5,
				 rmsMax = numpy.ones((2,),dtype=numpy.float),
				 rmsMin = numpy.zeros((2,),dtype=numpy.float)):
		self.sampleRate = sampleRate
		self.chunkSize = chunkSize 
		self.numChans = numChans
		self.rmsWindows = rmsWindows 
		self.rmsMax = rmsMax
		self.rmsMin = rmsMin
		self.rmsVals = rmsMin 
		self.currScore = numpy.zeros((numChans,),dtype = numpy.float)
		# instantiate pyAudio and open a stream for recording
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

		# this is supposed to just be a flag to control threads, don't know if
		# it will actually work like this or not
		self.isAcquiring = False
	
	#### handle the sound card and pyAudio stuff 
	#### start_recording and stop_recording are just acting as a switch
	def start_recording(self):
		# start the stream
		print 'recording started'
		self.theStream.start_stream()
		# fill self.rmsBuffer with some bullshit for now
		print 'stream started'
		for q in range(0,5):
			self.rmsBuffer.append(self.theStream.read(self.chunkSize))

		self.thr1 = threading.Thread(target=self.get_data)
		self.thr1.start()
		self.isAcquiring = True

	def stop_recording(self):
		self.isAcquiring = False
		time.sleep(0.1)
		self.theStream.close()
		self.p.terminate()

	def get_data(self):
		while True:
			if self.isAcquiring == False: 
				break
			# record the data into the deque array
			dataIn = self.theStream.read(self.chunkSize)
			# append the deque buffers
			self.timeStamp.append(time.time())
			self.rmsBuffer.append(dataIn)
			self.rawData.append(dataIn)
			
			# compute the rms and the normalized "score"
			self.compute_score()

	#### now do something with the acquired data

	def compute_score(self):
		dataString = ''.join(self.rmsBuffer)
				
		# unpack stream (16 bit) and convert to numpy array
		convertedData = numpy.array(struct.unpack(self.convertSamplesFormat,
												  dataString),
									dtype=numpy.float)/(2.**15)
		
		# channel data is interleaved (1 2 3 4 1 2 3 4...), so you have to take it apart
		convertedData = convertedData.reshape(convertedData.size/self.numChans,self.numChans)
		self.rmsVals = ((convertedData**2).mean(0))**0.5
		max_v = 0
		min_v = 0
		for val in self.rmsVals:
			if max_v < val:
				max_v = val
			
			if min_v > val:
				min_v = val
				
		# normalized(x_i) = (x_i - X_min) / (X_max - X_min)		
		in range:
			code
		

		# this just converts the rms values into a normalized score, 0-1 to do
		# something with later
		# adjust according to min/max rms values
		
		#self.rmsVals[self.rmsVals < self.rmsMin] = (
	#			self.rmsMin[self.rmsVals < self.rmsMin])
	#	self.rmsVals[self.rmsVals > self.rmsMax] = (
	#			self.rmsMax[self.rmsVals > self.rmsMax])


			


		# now get a percentage
		slope = 1 / (self.rmsMax-self.rmsMin)
		intercept = -1*self.rmsMin*slope
		self.currScore = slope*self.rmsVals+intercept
