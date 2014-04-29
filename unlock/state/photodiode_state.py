import time
from unlock.state.state import UnlockState

__author__ = 'Graham Voysey'


class PhotodiodeScopeState(UnlockState):
    DISPLAY_AT_REST = 0
    DISPLAY_RECORDING = 1
    DISPLAY_RECORDED = 2
    def __init__(self, data_table, analyzers, window_length):
        super(PhotodiodeScopeState, self).__init__()
        self.state = PhotodiodeScopeState.DISPLAY_AT_REST
        self.data_table = data_table
        self.analyzers = analyzers
        self.window_length = window_length
        self.start_time = -1

    def process_command(self, command):
        if command.selection:
            print('photodiode:process_command entered', self.state, command.selection)
        if self.state == PhotodiodeScopeState.DISPLAY_AT_REST and command.selection:  #command.selection: "someone has hit the spacebar"
            self.state = PhotodiodeScopeState.DISPLAY_RECORDING
            self.start_time = time.now()
        elif self.state == PhotodiodeScopeState.DISPLAY_RECORDING and not command.selection:
            self.state = PhotodiodeScopeState.DISPLAY_AT_REST
        elif self.state == PhotodiodeScopeState.DISPLAY_RECORDING:
            assert self.start_time >0


        return self.state

    def get_state(self):

        return self.state
