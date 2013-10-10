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

from .classify import UnlockClassifier
import numpy as np


class RootMeanSquare(UnlockClassifier):
	Left = 0
	Bottom = 1
	Right = 2
	Select = 3
	def __init__(self, rms_thresholds, channels=4, window_size=22050, shift_size=512, filters=None):
		super(RootMeanSquare, self).__init__()
		self.left_thres = thresholds[RootMeanSquare.Left]
		self.bottom_thres = thresholds[RootMeanSquare.Bottom]
		self.right_thres = thresholds[RootMeanSquare.Right]		
		self.channels = channels
		self.window_size = window_size
		self.shift_size = shift_size
		self.filters = filters
		self.window = np.zeros((channels, window_size))
		self.shift = np.zeros((channels, shift_size))
		self.current_size = 0
	
	def is_left(self, chan0, chan1, chan2):
		if chan0 > self.left_thres and chan1 < self.bottom_thres and chan2 < self.right_thres:
			return True
		else:
			return False		
	def is_right(self, chan0, chan1, chan2):
		if chan0 < self.left_thres and chan1 < self.bottom_thres and chan2 > self.right_thres:
			return True
		else:
			return False		
	def is_back(self, chan0, chan1, chan2):
		if chan0 > self.left_thres and chan1 < self.bottom_thres and chan2 > self.right_thres:
			return True
		else:
			return False
	def is_forward(self, chan0, chan1, chan2):
		if chan0 > self.left_thres and chan1 > self.bottom_thres and chan2 > self.right_thres:
			return True
		else:
			return False
	
	def classify(self, command):
		if not command.is_valid():
			return command
	
		self.window = np.roll(self.window, -1*command.data_matrix.size, axis=0)
		for row in self.window:
			self.window[row] = command.data_matrix[row]
			
		rms = self.window**2
		chan0 = rms[:, :1].mean()**0.5
		chan1 = rms[:, 1:2].mean()**0.5
		chan2 = rms[:, 2:3].mean()**0.5
		chan3 = rms[:, 3:4].mean()**0.5         
		if self.is_left(chan0, chan1, chan2):
			command.decision = 1
		elif self.is_right(chan0, chan1, chan2):
			command.decision = 2
		elif self.is_back(chan0, chan1, chan2):
			command.decision = 3
		elif self.forward(chan0, chan1, chan2):
			command.decision = 4
			
		return command