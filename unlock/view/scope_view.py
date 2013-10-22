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

from .view import UnlockView


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

        self.cursor = self.drawLine(self.xlim[0], self.ylim[0],
                                    self.xlim[0], self.ylim[1],
                                    canvas.batch, color=(255, 0, 0))

    def render(self):
        cursor_pos, traces = self.model.get_state()
        self.cursor.vertices[::2] = self.xlim + cursor_pos


class LinePlotView(UnlockView):
    def __init__(self, model, canvas):
        super(LinePlotView, self).__init__()
        self.model = model

    def render(self):
        state = self.model.get_state()
        if not state:
            return
        #self.line.vertices[1::2] = [i + self.y for i in lines]



