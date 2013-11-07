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
import numpy as np
import time


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
        self.trace_margin = 0.1 * self.trace_height
        self.trace_height -= self.trace_margin
        self.yscale = self.trace_height / 200

        self.traces = []
        for trace in range(self.model.n_channels):
            x = self.scale_width(np.arange(0, self.model.n_samples))
            y = self.scale_height(np.zeros(self.model.n_samples),
                                  0, 1, trace)
            values = zip(x, y)
            vertices = [point for points in values for point in points]
            self.traces.append(self.drawLinePlot(vertices, canvas))

        self.cursor = self.drawLine(self.xlim[0], self.ylim[0],
                                    self.xlim[0], self.ylim[1],
                                    canvas, color=(255, 0, 0))

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
        offset = self.ylim[0] + 0.5*self.trace_height + \
            trace*(self.trace_height + self.trace_margin)
        y = (y - shift) * scale
        return y * self.yscale + offset

    def render(self):
        update, cursor_pos, y_data, shift, scale = self.model.get_state()
        if update:
            x = self.scale_width(cursor_pos)
            self.cursor.vertices[::2] = (x,)*2
            for i, trace in enumerate(self.traces):
                y = self.scale_height(y_data[:, i], shift[i], scale, i)
                data_points = len(y)
                y_points = np.zeros(len(trace.vertices)/2)
                for j in range(data_points-1):
                    y_points[[j*2, j*2+1]] = y[j:j+2]
                trace.vertices[1::2] = y_points


class FrequencyScopeView(UnlockView):
    def __init__(self, model, canvas, labels=None):
        """
        the scope view has n_channel traces w/ labels and a single cursor bar
        additionally having range indicators would be good
        """
        super(FrequencyScopeView, self).__init__()

        self.model = model

        self.xlim = (canvas.width*0.05, canvas.width*0.95)
        self.ylim = (canvas.height*0.05, canvas.height*0.95)

        plot_points = len(self.model.trace)
        display_channels = len(self.model.display_channels)
        self.xscale = (self.xlim[1]-self.xlim[0])/plot_points
        self.trace_height = (self.ylim[1]-self.ylim[0])/display_channels
        self.trace_margin = 0.1 * self.trace_height
        self.trace_height -= self.trace_margin
        self.yscale = self.trace_height

        self.traces = []
        self.axes = []
        for trace in range(display_channels):
            x = self.scale_width(np.arange(0, plot_points))
            y = self.scale_height(np.zeros(plot_points),
                                  0, 1, trace)
            values = zip(x, y)
            vertices = [point for points in values for point in points]
            self.traces.append(self.drawLinePlot(vertices, canvas))
            if labels is None:
                freq_labels = np.linspace(self.model.freq_begin,
                                          self.model.freq_end, 5)
                labels = ["%.2f" % f for f in freq_labels]
            self.axes.append(self.generate_axis(
                x[0], y[0], x[-1], y[0], canvas, labels=labels))

    def generate_axis(self, x1, y1, x2, y2, canvas, ticks=None, labels=None):
        lines = list()
        lines.append(self.drawLine(x1, y1, x2, y2, canvas))
        if ticks is None and labels is not None:
            ticks = len(labels)
        if ticks is not None:
            x_points = np.linspace(x1, x2, ticks)
            for x in x_points:
                lines.append(self.drawLine(x, y1, x, y1 - 10, canvas))
        if labels is not None:
            x_points = np.linspace(x1, x2, len(labels))
            for i, x in enumerate(x_points):
                lines.append(self.drawText(str(labels[i]), x, y1 - 15, canvas,
                                           size=12))
        return lines


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
        offset = self.ylim[0] + 0.05*self.trace_height + \
            trace*(self.trace_height + self.trace_margin)
        y = (y - shift) * scale
        return y * self.yscale + offset

    def render(self):
        update, y_data = self.model.get_state()
        if update:
            for i, trace in enumerate(self.traces):
                y = self.scale_height(y_data[:, i], 0, 1, i)
                data_points = len(y)
                y_points = np.zeros(len(trace.vertices)/2)
                for j in range(data_points-1):
                    y_points[[j*2, j*2+1]] = y[j:j+2]
                trace.vertices[1::2] = y_points