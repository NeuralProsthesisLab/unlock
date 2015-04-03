"""
This is the hardcoded app setup for the cVEP BCI experiment trials. It is for the cued phase only. There
are three different paradigms: 4-choice overt, 2-choice covert, and 2-choice gaze independent. In all three cases,
a template match based decoding approach will be used. These templates will be generated through an initial training
phase.

Training
cue target. present target for 5-12 seconds. provide qualitative feedback during training to indicate consistency of
templates. Only run as long as needed to get high accuracy templates or for a fixed (~5 min) period.

Testing
cue target. prep period. trial display (stop when confident or ~3 sec). feedback. rest.
"""
import numpy as np

from unlock.state import UnlockState, TimerState


class CueState:
    duration = 0.4
    size = 200
    hold = False

    @staticmethod
    def next(state):
        state.trial_count += 1
        return PrepState


class CueUpState(CueState):
    marker = 2
    label = '\u21e7'


class CueDownState(CueState):
    marker = 3
    label = '\u21e9'


class CueLeftState(CueState):
    marker = 4
    label = '\u21e6'


class CueRightState(CueState):
    marker = 5
    label = '\u21e8'


class PrepState:
    marker = 6
    duration = 0.4
    label = '+'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        state.stimuli.start()
        return TrialState


class TrialState:
    marker = 7
    duration = 1.1
    label = '+'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        state.stimuli.stop()
        for stimulus in state.stimuli.stimuli:
            stimulus.state = None

        if np.random.choice([True, False]):
            return FeedbackGoodState
        else:
            return FeedbackBadState


class FeedbackState:
    duration = 0.4
    size = 120
    hold = False

    @staticmethod
    def next(state):
        return RestState


class FeedbackGoodState(FeedbackState):
    marker = 8
    label = '\u2714'


class FeedbackBadState(FeedbackState):
    marker = 9
    label = '\u2718'


class RestState:
    marker = 10
    duration = 0.4
    label = ''
    size = 48
    hold = False

    @staticmethod
    def next(state):
        if state.trial_count >= state.trials_per_block:
            return BlockEndState
        else:
            return state.next_cue()


class BlockStartState:
    marker = 11
    duration = 2
    label = 'Block Start'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        state.trial_count = 0
        return state.next_cue()


class BlockEndState:
    marker = 12
    duration = 0
    label = 'Press space bar to continue.'
    size = 48
    hold = True

    @staticmethod
    def next(state):
        return BlockStartState


class ExperimentStartState:
    marker = 0
    duration = 0
    label = ''
    size = 48
    hold = False

    @staticmethod
    def next(state):
        state.stimuli.stop()
        for stimulus in state.stimuli.stimuli:
            stimulus.state = None
        return BlockStartState


class ExperimentState(UnlockState):
    def __init__(self, stimuli, outlet):
        super(ExperimentState, self).__init__()
        self.state = ExperimentStartState
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

        self.trials_per_block = 4
        self.trial_count = 0

        self.stimuli = stimuli
        self.outlet = outlet

    def get_state(self):
        if self.state_change:
            self.state_change = False
            return self.state

    def next_cue(self):
        return np.random.choice([CueUpState, CueDownState, CueLeftState, CueRightState])

    def next_state(self):
        self.state = self.state.next(self)
        self.outlet.push_sample([self.state.marker])
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def process_command(self, command):
        if self.state.hold:
            if command.selection:
                self.next_state()
        else:
            self.timer.update_timer(command.delta)
            if self.timer.is_complete():
                self.next_state()