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
from .model import UnlockModel


class TimeScopeState(UnlockModel):
    def __init__(self, n_channels, fs, duration=2):
        super(TimeScopeState, self).__init__()
        self.n_channels = n_channels
        self.fs = fs
        self.duration = duration
        self.n_samples = self.duration * self.fs

        self.cursor = 0
        self.traces = np.zeros((self.n_samples, self.n_channels))
        self.yscale = 1
        self.yshift = 0

    def get_state(self):
        return self.cursor, self.traces, self.yshift, self.yscale

    def process_command(self, command):
        if not command.is_valid():
            return

        samples = command.matrix[:, 0:self.n_channels]
        s = samples.shape[0]
        idx = np.arange(self.cursor, self.cursor+s) % self.n_samples
        self.traces[idx] = samples
        last_cursor = self.cursor
        self.cursor += s
        self.cursor %= self.n_samples
        if self.cursor < last_cursor:
            max = np.max(self.traces)
            scale = np.round(0.5*(max - np.min(self.traces)), 2)
            shift = max - scale
            if scale != 0:
                if 0.9*self.yscale < scale / 100.0 < 1.1*self.yscale:
                    pass
                else:
                    self.yscale = scale / 100.0
                if 0.9*self.yshift < shift < 1.1*self.yshift:
                    pass
                else:
                    self.yshift = shift




class LinePlotState(UnlockModel):
    def __init__(self):
        super(LinePlotState, self).__init__()


    def updateData(self, y_data, offset=0):
        points = len(y_data)
        lines = y_data[0:2]
        for i in range(1,points-1):
            lines.extend([y_data[i],y_data[i+1]])
        self.line.vertices[1::2] = [i + self.y for i in lines]
#        self.line.vertices[1] = y_data[0] + self.y
#        self.line.vertices[3:-2:2] = [i + self.y for i in y_data]
#        self.line.vertices[-1] = y_data[-1] + self.y_data
