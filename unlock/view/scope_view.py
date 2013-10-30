# Copyright (c) Byron Galbraith, James Percent,  and Unlock contributors.
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

from unlock.view.view import UnlockView


class TimeScopeView(UnlockView):
    def __init__(self, model, canvas, labels=None):
        """
        the scope view has n_channel traces w/ labels and a single cursor bar
        additionally having range indicators would be good
        """
        super(TimeScopeView, self).__init__()

        self.model = model

        self.xlim = (canvas.width*0.05, canvas.width*0.95)
        self.ylim = (canvas.height*0.05, canvas.height*0.95)

        self.xscale = (self.xlim[1]-self.xlim[0])/float(self.model.n_samples)
        self.trace_height = (self.ylim[1]-self.ylim[0])/float(self.model.n_channels)
        self.trace_margin = 0.025 * self.trace_height
        self.trace_height -= self.trace_margin

        self.cursor = self.drawLine(self.xlim[0], self.ylim[0],
                                    self.xlim[0], self.ylim[1],
                                    canvas.batch, color=(255, 0, 0))

    def scale_width(self, x):
        """
        Scale the position of the data points to fit the width of the screen
        """
        return x * self.xscale + self.xlim[0]

    def scale_height(self, y, shift, scale, trace=0):
        """
        Scale the position of the data points to fit the height of the screen
        and the number of traces. The scale factor is automatically adjusted
        to the data, and is thus part of the model.
        """
        offset = self.ylim[0] + trace*(self.trace_height + 2*self.trace_margin)
        return (y - shift) / scale + offset

    def render(self):
        cursor_pos, traces, shift, scale = self.model.get_state()
        x = self.scale_width(cursor_pos)
        self.cursor.vertices[::2] = (x,)*2


class LinePlotView(UnlockView):
    def __init__(self, model, canvas):
        super(LinePlotView, self).__init__()
        self.model = model

    def render(self):
        state = self.model.get_state()
        if not state:
            return
        #self.line.vertices[1::2] = [i + self.y for i in lines]



