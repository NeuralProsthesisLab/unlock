import time
from unlock.state.state import UnlockState
import numpy as np
__author__ = 'Graham Voysey'


class PhotodiodeScopeState(UnlockState):
    DISPLAY_AT_REST = 0
    DISPLAY_RECORDING = 1
    DISPLAY_RECORDED = 2

    def __init__(self, data_table, analyzer, window_length,spectrogram_filename):
        super(PhotodiodeScopeState, self).__init__()
        self.state = PhotodiodeScopeState.DISPLAY_AT_REST
        self.data_table = data_table
        self.analyzer = analyzer
        self.window_length = window_length
        self.start_time = -1
        self.spectrogram_filename = spectrogram_filename

    def process_command(self, command):
        if self.state == PhotodiodeScopeState.DISPLAY_AT_REST and command.selection:  #command.selection: "someone has hit the spacebar"
            self.state = PhotodiodeScopeState.DISPLAY_RECORDING
            self.start_time = time.time()
            if(command.is_valid()):
                self.data_table.raw_data = command.matrix
        elif self.state == PhotodiodeScopeState.DISPLAY_RECORDING and not command.selection:
            if self.data_table.raw_data is None and command.is_valid():
                self.data_table.raw_data = command.matrix
            elif command.is_valid():
                self.data_table.raw_data = np.concatenate((self.data_table.raw_data, command.matrix))
                if abs(self.start_time - time.time()) >= self.window_length:
                    self.analyzer.file_name = self.spectrogram_filename
                    print("COMPUTING spectrogram ", self.analyzer.file_name)
                    print("data table = ", self.data_table.signal_rows())
                    self.analyzer.analyze()
                    self.state = PhotodiodeScopeState.DISPLAY_RECORDED
        elif self.state > PhotodiodeScopeState.DISPLAY_AT_REST and command.selection:
            assert self.start_time > 0
            self.state = PhotodiodeScopeState.DISPLAY_AT_REST
            return self.state
        elif self.state == PhotodiodeScopeState.DISPLAY_RECORDED and not command.selection:
            self.state = PhotodiodeScopeState.DISPLAY_RECORDING
            self.start_time = time.time()
            self.data_table.raw_data = command.matrix
        return self.state

    def get_state(self):

        return self.state
