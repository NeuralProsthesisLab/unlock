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
from unlock.state import TimerState


class GazeDecoder(UnlockDecoder):
    def __init__(self, raw=False, eyeblink_calibration=None):
        super(GazeDecoder, self).__init__()
        self.n_electrodes = 8
        self.buffer = np.zeros((10, 2))
        self.raw = raw

        if eyeblink_calibration is None:
            self.detect_eyeblinks = False
        else:
            self.detect_eyeblinks = True
            self.double_blink = eyeblink_calibration["double_blink"]
            self.triple_blink = eyeblink_calibration["triple_blink"]

            self.skip_counter = 0
            self.skip_threshold = 10
            self.gaze_detected = True
            self.gaze_events = np.zeros(2)
            self.double_detected = False
            self.triple_detected = False
            self.blinks = 0
            # hold_duration = (self.double_blink[1, 1] + self.triple_blink[1, 1] +
            #         self.triple_blink[1, 3]) / 3
            # self.blink_duration = (np.sum(self.double_blink[1, [0, 2]]) +
            #                   np.sum(self.triple_blink[1, [0, 2, 4]])) / 5
            self.blink_duration = 1.0
            self.hold_duration = 0.4
            self.hold_timer = TimerState(self.hold_duration)

    def decode(self, command):
        if not command.is_valid():
            return command
        gaze_data = command.matrix[:, self.n_electrodes:self.n_electrodes+2]
        gaze_pos = np.where(gaze_data[:, 0] != 0)[0]
        samples = len(gaze_pos)

        if self.detect_eyeblinks:
            if self.blinks > 0:
                self.hold_timer.update_timer(command.delta)
                if self.hold_timer.is_complete():
                    if self.blinks == 2:
                        # print(self.blinks)
                        command.selection = True
                    elif self.blinks == 3:
                        # print(self.blinks)
                        command.stop = True
                    self.blinks = 0
            self.detect_gaze_event(samples)
            # if self.triple_detected:
            #     self.triple_detected = False
            #     command.stop = True
            # elif self.double_detected:
            #     self.hold_timer.update_timer(command.delta)
            #     if self.hold_timer.is_complete():
            #         self.double_detected = False
            #         command.selection = True

        if samples == 0:
            return command

        if not self.raw:
            self.buffer = np.roll(self.buffer, -samples, axis=0)
            self.buffer[-samples:] = gaze_data[gaze_pos]
            command.gaze = np.mean(self.buffer, axis=0)
        else:
            command.gaze = gaze_data[gaze_pos[-1]]
        return command

    def detect_gaze_event(self, samples):
        now = time.time()
        if samples == 0:
            self.skip_counter += 1
            if self.gaze_detected and self.skip_counter >= self.skip_threshold:
                self.gaze_detected = False
                # self.gaze_events = np.roll(self.gaze_events, -1)
                self.gaze_events[0] = now
        else:
            self.skip_counter = 0
            if not self.gaze_detected:
                self.gaze_detected = True
                # self.gaze_events = np.roll(self.gaze_events, -1)
                self.gaze_events[1] = now
                if np.diff(self.gaze_events)[0] <= self.blink_duration:
                    # print("blink")
                    self.blinks += 1
                    self.hold_timer.begin_timer()
                # self.classify_blinks()

    # def classify_blinks(self):
    #     self.blinks += 1
    #     if not self.double_detected:
    #         dbl_blink = np.diff(self.gaze_events[-4:])
    #
    #         if ((dbl_blink >= 2*self.double_blink[0]) &
    #            (dbl_blink <= 2*self.double_blink[1])).all():
    #             print("double blink")
    #             self.double_detected = True
    #             self.hold_timer.begin_timer()
    #
    #     tpl_blink = np.diff(self.gaze_events)
    #     if ((tpl_blink >= 2*self.triple_blink[0]) &
    #        (tpl_blink <= 2*self.triple_blink[1])).all():
    #         self.triple_detected = True
    #         self.double_detected = False

