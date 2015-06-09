"""
We want to collect gaze data while prompting the user to perform intentional
double and triple blinks. After a trial, the duration of the blinks and spacing
between them should be computed and used to build the user's eye blink profile
"""
import time

import numpy as np

from unlock.state.state import UnlockState


class EyeBlinkCalibrationState(UnlockState):
    def __init__(self):
        super(EyeBlinkCalibrationState, self).__init__()
        self.state_change = False
        self.state = None

        self.skip_counter = 0
        self.skip_threshold = 10

        self.trial_idx = 0
        self.n_trials = 5
        self.gaze_events = np.zeros((self.n_trials, 6))
        # self.gaze_events = np.zeros((self.n_trials, 6))
        self.blinks = 0
        self.started = False
        self.gaze_detected = True
        self.trial_start = None
        self.trial_time = 3.0

    def start(self):
        self.gaze_detected = True
        self.blinks = 0
        self.started = True
        self.trial_start = time.time()

    def get_state(self):
        if self.state_change:
            self.state_change = False
            return self.state

    def process_command(self, command):
        if not self.started or not command.is_valid():
            return command

        gaze_data = command.matrix[:, 8:10]
        gaze_pos = np.where((gaze_data[:, 0] > 0) & (gaze_data[:, 1] > 0))[0]
        samples = len(gaze_pos)
        now = time.time()

        if samples == 0:
            self.skip_counter += 1
            if self.gaze_detected and self.skip_counter >= self.skip_threshold:
                self.gaze_detected = False
                self.gaze_events[self.trial_idx, 2*self.blinks] = now
        else:
            self.skip_counter = 0
            if not self.gaze_detected:
                self.gaze_detected = True
                self.gaze_events[self.trial_idx, 2*self.blinks+1] = now
                self.blinks += 1
            if self.blinks == 3:
                self.blinks = 0
                self.trial_idx += 1
                if self.trial_idx >= self.n_trials:
                    print("blinks:", np.mean(np.diff(self.gaze_events), axis=0),
                          np.std(np.diff(self.gaze_events), axis=0))
                    self.trial_idx = 0

        self.state = command.gaze
        self.state_change = True
