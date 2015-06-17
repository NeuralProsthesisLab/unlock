"""
We want to collect gaze data while prompting the user to perform intentional
double and triple blinks. After a trial, the duration of the blinks and spacing
between them should be computed and used to build the user's eye blink profile
"""
import time

import numpy as np

from unlock.state.state import UnlockState, TimerState


class EyeBlinkCalibrationState(UnlockState):
    def __init__(self, subject_id):
        super(EyeBlinkCalibrationState, self).__init__()
        self.subject_id = subject_id

        self.skip_counter = 0
        self.skip_threshold = 10

        self.trial_idx = 0
        self.n_trials = 10
        self.n_blinks = 2

        self.gaze_events = np.zeros((self.n_trials, 6))
        self.blinks = 0
        self.gaze_detected = True

        self.steps = (CueDoubleState, CueTripleState, CalibrationEndState)
        self.step = 0

        self.state = CalibrationStartState
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def get_state(self):
        if self.state_change:
            self.state_change = False
            return self.state

    def next_state(self):
        self.state = self.state.next(self)
        self.state.enter(self)
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def process_command(self, command):
        if self.state.hold:
            if command.selection:
                self.next_state()
            return command

        self.timer.update_timer(command.delta)
        if self.timer.is_complete():
            self.next_state()

        if self.state is not TrialState or self.blinks >= self.n_blinks or \
                not command.is_valid():
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


class CalibrationStartState:
    text = 'Press space bar to continue'
    duration = 0.0
    hold = True

    @staticmethod
    def next(state):
        return CueDoubleState

    @staticmethod
    def enter(state):
        pass


class CalibrationEndState:
    text = 'All done. Thanks!'
    duration = 0.0
    hold = True

    @staticmethod
    def next(state):
        return CalibrationEndState

    @staticmethod
    def enter(state):
        mu_dbl_blink = np.mean(np.diff(state.gaze_events[0:5, 0:4]), axis=0)
        sigma_dbl_blink = np.std(np.diff(state.gaze_events[0:5, 0:4]), axis=0)
        mu_tpl_blink = np.mean(np.diff(state.gaze_events[5:]), axis=0)
        sigma_tpl_blink = np.std(np.diff(state.gaze_events[5:]), axis=0)

        double_blink = [mu_dbl_blink - sigma_dbl_blink,
                        mu_dbl_blink + sigma_dbl_blink]

        triple_blink = [mu_tpl_blink - sigma_tpl_blink,
                        mu_tpl_blink + sigma_tpl_blink]

        print("double blinks:", mu_dbl_blink, sigma_dbl_blink)
        print("triple blinks:", mu_tpl_blink, sigma_tpl_blink)
        np.savez("%s-eyeblink_calibration" % state.subject_id,
                 double_blink=double_blink, triple_blink=triple_blink)

class TrialState:
    text = ''
    duration = 2.0
    hold = False

    @staticmethod
    def next(state):
        if state.blinks >= state.n_blinks:
            state.trial_idx += 1

            if state.trial_idx % 5 == 0:
                state.step += 1
                state.n_blinks = 3
        return state.steps[state.step]

    @staticmethod
    def enter(state):
        state.gaze_detected = True
        state.blinks = 0


class CueState:
    text = ''
    duration = 0.5
    hold = False

    @staticmethod
    def next(state):
        return TrialState

    @staticmethod
    def enter(state):
        pass


class CueDoubleState(CueState):
    text = 'Double Blink'


class CueTripleState(CueState):
    text = 'Triple Blink'
