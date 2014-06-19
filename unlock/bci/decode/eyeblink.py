# Copyright (c) Byron Galbraith and Unlock contributors.
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

from unlock.bci.decode.decode import UnlockDecoder
import numpy as np
import time


class EyeBlinkDetector(UnlockDecoder):
    NoEvent = 0
    SelectionEvent = 1
    EscapeEvent = 2

    def __init__(self, eog_channels=(5, 7), strategy='length',
                 rms_threshold=60000):
        super(EyeBlinkDetector, self).__init__()

        # blink detection method
        if strategy == 'length':
            self.blink_strategy = BlinkLengthStrategy(rms_threshold, 1, 2)
        else:
            self.blink_strategy = BlinkCountStrategy(rms_threshold, 0.5, 0.75)

        self.eog_channels = eog_channels
        
        # adaptive demean
        self.mu = 0
        self.alpha = 0.05
        
        # blink settings
        self.rms_window = 50
        self.sample_buffer = np.zeros(self.rms_window)
        
    def decode(self, command):
        if not command.is_valid():
            return command
            
        samples = np.mean(command.matrix[:, self.eog_channels], axis=1)
        s = samples.shape[0]
            
        for i in range(s):
            self.mu = (1-self.alpha)*self.mu + self.alpha*samples[i]
            samples[i] -= self.mu

        if s >= len(self.sample_buffer):
            s = len(self.sample_buffer)
        self.sample_buffer = np.roll(self.sample_buffer, -s)
        self.sample_buffer[-s:] = samples[-s:]
            
        rms = np.sqrt(np.mean(self.sample_buffer**2))

        result = self.blink_strategy.process_rms(rms)
        if result == EyeBlinkDetector.SelectionEvent:
            command.selection = True
        elif result == EyeBlinkDetector.EscapeEvent:
            command.stop = True
        return command


class BlinkLengthStrategy:
    def __init__(self, rms_threshold, short_blink_time, long_blink_time):
        """
        Events are determined by the length of a single intentional blink.
        """
        # event parameters
        self.rms_threshold = rms_threshold
        self.short_blink_time = short_blink_time  # selection event
        self.long_blink_time = long_blink_time  # escape event

        # state variables
        self.short_blink_notified = False
        self.blink_time_start = 0
        self.blink_event = EyeBlinkDetector.NoEvent

    def reset(self):
        self.short_blink_notified = False
        self.blink_time_start = 0
        self.blink_event = EyeBlinkDetector.NoEvent

    def process_rms(self, rms):
        if rms < self.rms_threshold and self.blink_time_start == 0:
            return

        if rms > self.rms_threshold:
            now = time.time()
            if self.blink_time_start == 0:
                self.blink_time_start = now

            if now >= self.blink_time_start + self.long_blink_time:
                # TODO: notify user long blink occurred
                self.blink_event = EyeBlinkDetector.EscapeEvent
            elif (not self.short_blink_notified and
                  now >= self.blink_time_start + self.short_blink_time):
                # TODO: notify user short blink occurred
                self.short_blink_notified = True
                self.blink_event = EyeBlinkDetector.SelectionEvent
        elif self.blink_event != EyeBlinkDetector.NoEvent:
            print('blink event:', self.blink_event)
            ret = self.blink_event
            self.reset()
            return ret
        else:
            self.reset()


class BlinkCountStrategy:
    def __init__(self, rms_threshold, min_blink_interval, max_blink_interval):
        """
        Events are determined by the number of intentional repetitive blinks.
        """
        # event parameters
        self.rms_threshold = rms_threshold
        self.min_blink_interval = min_blink_interval
        self.max_blink_interval = max_blink_interval

        # state variables
        self.blink_count = 0
        self.last_blink_time = time.time()
        self.blink_event = EyeBlinkDetector.NoEvent

    def reset(self):
        self.blink_count = 0
        self.last_blink_time = time.time()
        self.blink_event = EyeBlinkDetector.NoEvent

    def process_rms(self, rms):
        if rms < self.rms_threshold and self.blink_count == 0:
            return

        now = time.time()
        if rms >= self.rms_threshold:
            if now >= self.last_blink_time + self.min_blink_interval:
                self.blink_count += 1
                self.last_blink_time = now
        elif now >= self.last_blink_time + self.max_blink_interval:
            if self.blink_count > 1:
                if self.blink_count == 2:
                    self.blink_event = EyeBlinkDetector.SelectionEvent
                elif self.blink_count == 3:
                    self.blink_event = EyeBlinkDetector.EscapeEvent
                print('blink event:', self.blink_event)
                ret = self.blink_event
                self.reset()
                return ret
            else:
                self.reset()