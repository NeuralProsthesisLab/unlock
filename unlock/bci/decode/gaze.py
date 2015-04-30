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
import time

import numpy as np

from unlock.bci.decode.decode import UnlockDecoder


class GazeDecoder(UnlockDecoder):
    def __init__(self):
        super(GazeDecoder, self).__init__()
        self.n_electrodes = 8
        self.buffer = np.zeros((10, 2))

        self.detect_eyeblinks = True
        self.last_gaze_detected = 0
        self.last_blink_detected = 0
        self.blinks = 0
        self.min_blink_length = 0.2
        self.max_blink_length = 0.5
        self.max_blink_interval = 0.5

    def decode(self, command):
        if not command.is_valid():
            return command
        gaze_data = command.matrix[:, self.n_electrodes:self.n_electrodes+2]
        gaze_pos = np.where(gaze_data[:, 0] != 0)[0]
        samples = len(gaze_pos)
        if samples == 0:
            self.last_gaze_detected += command.delta
            return command

        if self.detect_eyeblinks:
            if self.min_blink_length <= self.last_gaze_detected <= self.max_blink_length:
                self.blinks += 1
                self.last_blink_detected = time.time()
            elif time.time() - self.last_blink_detected > self.max_blink_interval:
                if self.blinks > 1:
                    if self.blinks == 2:
                        command.selection = True
                    if self.blinks == 3:
                        command.stop = True
                self.blinks = 0
                self.last_blink_detected = 0
        self.last_gaze_detected = 0

        self.buffer = np.roll(self.buffer, -samples, axis=0)
        self.buffer[-samples:] = gaze_data[gaze_pos]

        command.gaze = np.mean(self.buffer, axis=0)

        return command