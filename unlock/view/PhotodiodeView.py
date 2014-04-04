__author__ = 'Graham Voysey'
from unlock.view.view import UnlockView


class PhotodiodeView(UnlockView):
    def __init__(self, model, canvas, labels=None):
        self.model = model
        self.xlim = (canvas.width * 0.05, canvas.width * 0.95)
        self.ylim = (canvas.height * 0.05, canvas.height * 0.95)

        plot_points = len(self.model.trace)
        display_channels = len(self.model.display_channels)
        self.xscale = (self.xlim[1] - self.xlim[0]) / plot_points
        self.trace_height = (self.ylim[1] - self.ylim[0]) / display_channels
        self.trace_margin = 0.1 * self.trace_height
        self.trace_height -= self.trace_margin
        self.yscale = self.trace_height

        self.traces = []
        self.axes = []