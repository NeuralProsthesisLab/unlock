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

from .classify import UnlockClassifier
import numpy as np

class EyeBlinkDetector(UnlockClassifier):
    def __init__(self):
        super(EyeBlinkDetector, self).__init__()
        
        ## enobio setup: 5 - left eye, 7 - right eye
        self.eog_channels = [5, 7]
        
        # adaptive demean
        self.mu = 0
        self.alpha = 0.05
        
        # blink settings
        self.threshold = 60000  # rms window threshold
        self.long_blink_time = 1000  # number of samples - 2s
        self.short_blink_time = 500 # number of samples - 1s
        self.short_blink_notified = False
        self.blink_timer = 0 # sample counter
        self.blink_action = 0 # action id, should be enum or function
        self.rms_window = 50
        self.sample_buffer = np.zeros(self.rms_window)
        
    def classify(self, command):
        if not command.is_valid():
            return command
            
        samples = np.mean(command.matrix[:, self.eog_channels], axis=1)
        s = samples.shape[0]
            
        for i in range(s):
            self.mu = (1-self.alpha)*self.mu + self.alpha*samples[i]
            samples[i] -= self.mu
            
        self.sample_buffer = np.roll(self.sample_buffer, -s)
        self.sample_buffer[-s:] = samples
            
        rms = np.sqrt(np.mean(self.sample_buffer**2))
            
        if rms > self.threshold:
            self.blink_timer += s
            if self.blink_timer >= self.long_blink_time:
                # notify user long blink occurred
                self.blink_action = 2
            elif not (self.short_blink_notified and
                      self.blink_timer >= self.short_blink_time):
                # notify user short blink occurred
                self.short_blink_notified = True
                self.blink_action = 1
        elif self.blink_action > 0:
            print('blink action:', self.blink_action)
            command.selection = True
            self.blink_action = 0
            self.short_blink_notified = False
        else:
            self.blink_timer = 0
            
        return command
        
        