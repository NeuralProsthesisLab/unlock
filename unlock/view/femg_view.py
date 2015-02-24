__author__ = 'Graham Voysey'
from unlock.view.view import UnlockView

class FEMGView(UnlockView):
    def __init__(self, state, canvas):
        super(FEMGView, self).__init__()
        self.state = state
        self.canvas = canvas
