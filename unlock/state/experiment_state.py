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


class ExperimentState(UnlockState):
    def __init__(self, stim1, stim2, outlet, block_sequence=None, trials_per_block=6):
        super(ExperimentState, self).__init__()
        self.stim1 = stim1
        self.stim2 = stim2
        self.current_stim = self.stim1
        self.outlet = outlet
        if block_sequence is None:
            self.n_blocks = 3
        else:
            self.n_blocks = len(block_sequence)
        self.trials_per_block = trials_per_block

        self.trial_sequence = None
        self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState, CueTileAState, CueTileBState]

        self.block_count = 0
        self.trial_count = 0

        self.stim1.stop()
        for stim in self.stim1.stimuli:
            stim.state = None
        self.stim2.stop()
        for stim in self.stim2.stimuli:
            stim.state = None

        self.state = ExperimentStartState
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def stop_stim(self):
        self.current_stim.stop()
        for stim in self.current_stim.stimuli:
            stim.state = None

    def start_stim(self):
        self.current_stim.start()

    def get_state(self):
        if self.state_change:
            self.state_change = False
            return self.state

    def next_cue(self):
        return self.cues[self.trial_sequence[self.trial_count]]

    def next_block(self):
        block = np.random.choice([BlockStartOvertState, BlockStartCovertState, BlockStartGazeState])
        if block is BlockStartGazeState:
            self.current_stim = self.stim2
            n_targets = 6
        else:
            self.current_stim = self.stim1
            n_targets = 6

        assert self.trials_per_block % n_targets == 0
        self.trial_sequence = np.random.permutation(
            np.repeat(np.arange(n_targets), self.trials_per_block / n_targets))
        return block

    def next_state(self):
        self.state = self.state.next(self)
        self.state.enter(self)
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
            if self.state is TrialState:
                self.current_stim.process_command(command)


class CueState:
    duration = 0.4
    size = 200
    hold = False

    @staticmethod
    def next(state):
        return PrepState

    @staticmethod
    def enter(state):
        state.trial_count += 1


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


class CueTileAState(CueState):
    marker = 5
    label = '\u25a3'
    color = (0, 255, 0, 255)


class CueTileBState(CueState):
    marker = 5
    label = '\u25a3'
    color = (255, 0, 255, 255)


class PrepState:
    marker = 6
    duration = 0.4
    label = '+'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        return TrialState

    @staticmethod
    def enter(state):
        pass


class TrialState:
    marker = 7
    duration = 5
    label = '+'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        if np.random.choice([True, False]):
            return FeedbackGoodState
        else:
            return FeedbackBadState

    @staticmethod
    def enter(state):
        state.start_stim()


class FeedbackState:
    duration = 0.4
    size = 120
    hold = False

    @staticmethod
    def next(state):
        return RestState

    @staticmethod
    def enter(state):
        state.stop_stim()


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

    @staticmethod
    def enter(state):
        pass


class BlockStartState:
    marker = 11
    duration = 2
    size = 48
    hold = False

    @staticmethod
    def next(state):
        return state.next_cue()

    @staticmethod
    def enter(state):
        state.block_count += 1
        state.trial_count = 0


class BlockStartOvertState(BlockStartState):
    marker = 11
    label = 'Overt'


class BlockStartCovertState(BlockStartState):
    marker = 12
    label = 'Covert'


class BlockStartGazeState(BlockStartState):
    marker = 13
    label = 'Gaze Independent'


class BlockEndState:
    marker = 14
    duration = 0
    label = 'Press space bar to continue.'
    size = 48
    hold = True

    @staticmethod
    def next(state):
        if state.block_count < state.n_blocks:
            return state.next_block()
        else:
            return ExperimentEndState

    @staticmethod
    def enter(state):
        pass


class ExperimentStartState:
    marker = 0
    duration = 0
    label = ''
    size = 48
    hold = False

    @staticmethod
    def next(state):
        return BlockEndState

    @staticmethod
    def enter(state):
        pass


class ExperimentEndState:
    marker = 0
    duration = 0
    label = 'All done. Thanks!'
    size = 48
    hold = True

    @staticmethod
    def next(state):
        return ExperimentEndState

    @staticmethod
    def enter(state):
        pass
