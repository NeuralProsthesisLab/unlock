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

from unlock.decode.classify.classify import UnlockClassifier
import numpy as np


class RootMeanSquare(UnlockClassifier):
	Left = 0
	Bottom = 1
	Right = 2
	Select = 3
	
	def __init__(self, rms_thresholds, channels=2, window_size=22050, shift_size=512, filters=None):
		super(RootMeanSquare, self).__init__()
		self.set_thresholds(rms_thresholds)
		self.channels = channels
		self.window_size = window_size
		self.shift_size = shift_size
		self.filters = filters
		self.window = np.zeros((window_size, channels))
		self.shift = np.zeros((shift_size, channels))
		self.current_size = 0
		
	def set_thresholds(self, rms_thresholds):
		if rms_thresholds == None:
			self.left_thres = None
			self.bottom_thres = None
			self.right_thres = None
		else:
			self.left_thres = thresholds[RootMeanSquare.Left]
			self.bottom_thres = thresholds[RootMeanSquare.Bottom]
			self.right_thres = thresholds[RootMeanSquare.Right]		
			
		
	def is_left(self, chan0, chan1, chan2, chan3):
		if chan0 > self.left_thres and chan1 < self.bottom_thres and chan2 < self.right_thres and chan3 < self.sel_thres:
			return True
		else:
			return False
			
	def is_right(self, chan0, chan1, chan2, chan3):
		if chan0 < self.left_thres and chan1 < self.bottom_thres and chan2 > self.right_thres and chan3 < self.sel_thres:
			return True
		else:
			return False
			
	def is_back(self, chan0, chan1, chan2, chan3):
		if chan0 > self.left_thres and chan1 < self.bottom_thres and chan2 > self.right_thres and chan3 < self.sel_thres:
			return True
		else:
			return False
			
	def is_forward(self, chan0, chan1, chan2, chan3):
		if chan0 > self.left_thres and chan1 > self.bottom_thres and chan2 > self.right_thres and chan3 < self.sel_thres:
			return True
		else:
			return False
			
	def is_select(self, chan0, chan1, chan2, chan3):
		if chan0 < self.left_thres and chan1 < self.bottom_thres and chan2 < self.right_thres and chan3 > self.sel_thres:
			return True
		else:
			return False
			
	def make_decision(self, chan0, chan1, chan2, chan3, command):
		if self.is_left(chan0, chan1, chan2, chan3):
			command.decision = 1
		elif self.is_right(chan0, chan1, chan2, chan3):
			command.decision = 2
		elif self.is_back(chan0, chan1, chan2, chan3):
			command.decision = 3
		elif self.forward(chan0, chan1, chan2, chan3):
			command.decision = 4
		elif self.is_select(chan0, chan1, chan2, chan3):
			command.selection = 1
			
		return command
		
	def classify(self, command):
		if not command.is_valid():
			return command
			
		self.window = np.roll(self.window, -1*command.data_matrix.size, axis=0)
		samples = len(command.data_matrix)
		for row in range(samples):
			self.window[row] = command.data_matrix[row]
			
		rms = self.window**2
		chan0 = rms[:, :1].mean()**0.5
		chan1 = rms[:, 1:2].mean()**0.5
		chan2 = rms[:, 2:3].mean()**0.5
		chan3 = rms[:, 3:4].mean()**0.5
		command.rms_data = (chan0, chan1, chan2, chan3)
		if self.left_thres != None:
			assert self.right_thres != None and self.bottom_thres != None
			command = self.make_decision(chan0, chan1, chan2, chan3, command)
				
		return command
		
		