from unlock.state.photodiode_state import PhotodiodeScopeState

__author__ = 'Graham Voysey'
from unlock.view.view import UnlockView


class PhotodiodeView(UnlockView):
    def __init__(self, model, canvas, resting_view, recording_view):
        self.model = model
        self.canvas = canvas
        self.resting_view = resting_view
        self.recording_view = recording_view

    def render(self):
        #callback reentry -- do screen manipulations here.
        if self.model.get_state() == PhotodiodeScopeState.DISPLAY_AT_REST:
            self.resting_view.model.state = True
            self.recording_view.model.state = False
        elif self.model.get_state() == PhotodiodeScopeState.DISPLAY_RECORDING:
            self.resting_view.model.state = False
            self.recording_view.model.state = True
        elif self.model.get_state() == PhotodiodeScopeState.DISPLAY_RECORDED:


        return
