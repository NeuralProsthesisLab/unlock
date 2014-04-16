__author__ = 'Graham Voysey'
from unlock.view.view import UnlockView


class PhotodiodeView(UnlockView):
    def __init__(self, model, canvas):
        self.model = model
        self.canvas = canvas

    def render(self):
        #callback reentry -- do screen manipulations here.
        return
