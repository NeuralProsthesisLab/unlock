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
    def __init__(self, mode, stim1, stim2, outlet, block_sequence, trials_per_block):
        super(ExperimentState, self).__init__()
        self.mode = mode
        self.stim1 = stim1
        self.stim2 = stim2
        self.current_stim = self.stim1
        self.outlet = outlet
        self.block_sequence = block_sequence
        self.n_blocks = len(block_sequence)
        self.blocks = [BlockStartOvertState, BlockStartCovertState, BlockStartGazeState]

        self.trials_per_block = trials_per_block

        self.trial_sequence = None
        self.cues = None
        self.fixations = None

        self.block_count = 0
        self.trial_count = 0

        self.stim1.stop()
        for stim in self.stim1.stimuli:
            stim.state = None
        self.stim2.stop()
        for stim in self.stim2.stimuli:
            stim.state = None

        self.state = ExperimentStartState
        self.outlet.push_sample([self.state.marker])
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

        self.decoder_scores = np.zeros(4)

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
        return self.cues[self.trial_sequence[self.trial_count][0]]

    def next_trial(self):
        return self.fixations[self.trial_sequence[self.trial_count][1]]

    def next_block(self):
        block_idx = self.block_sequence[self.block_count]
        block = self.blocks[block_idx]
        n_trials = self.trials_per_block[block_idx]
        if block is BlockStartGazeState:
            self.current_stim = self.stim2
            self.cues = [CueTileAState, CueTileBState, CueNullState]
            if self.mode == 'demo':
                self.cues = [CueTileAState, CueTileBState, CueNullState, CueTileAState, CueTileBState]
            self.fixations = [TrialStateCenter, TrialStateNE, TrialStateSE, TrialStateSW, TrialStateNW]
        else:
            self.current_stim = self.stim1
            self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState, CueNullState]
            self.fixations = [TrialStateCenter]
        n_targets = len(self.cues)
        n_fixations = len(self.fixations)

        assert n_trials % n_targets == 0
        assert n_trials % n_fixations == 0
        cue_order = np.repeat(np.arange(n_targets), int(n_trials / n_targets))
        fixation_order = np.tile(np.arange(n_fixations), int(n_trials / n_fixations))
        order = np.vstack((cue_order, fixation_order))
        self.trial_sequence = np.random.permutation(order.T)
        return block

    def next_state(self):
        self.state = self.state.next(self)
        self.state.enter(self)
        self.outlet.push_sample([self.state.marker])
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def process_command(self, command):
        self.decoder_scores = np.random.randint(0, 255, size=4)

        if self.state.hold:
            if command.selection:
                self.next_state()
        else:
            self.timer.update_timer(command.delta)
            if self.timer.is_complete():
                self.next_state()
            if self.state.__base__ is TrialState:
                self.current_stim.process_command(command)


class ExperimentTrainState(ExperimentState):
    def __init__(self, stim1, stim2, outlet, block_sequence=None, trials_per_block=20):
        super(ExperimentTrainState, self).__init__(stim1, stim2, outlet, block_sequence, trials_per_block)

    def next_cue(self):
        return self.cues[self.trial_sequence[self.trial_count]]

    def next_block(self):
        block = BlockStartOvertState #  np.random.choice([BlockStartOvertState, BlockStartCovertState, BlockStartGazeState])
        if block is BlockStartGazeState:
            self.current_stim = self.stim2
            n_targets = 2
        else:
            self.current_stim = self.stim1
            n_targets = 4

        assert self.trials_per_block % n_targets == 0
        self.trial_sequence = np.random.permutation(
            np.repeat(np.arange(n_targets), self.trials_per_block / n_targets))
        return block


class CueState:
    duration = 0.4
    size = 200
    hold = False

    @staticmethod
    def next(state):
        return PrepState

    @staticmethod
    def enter(state):
        pass


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
    marker = 2
    label = '\u25a3'
    color = (0, 255, 0, 255)


class CueTileBState(CueState):
    marker = 3
    label = '\u25a3'
    color = (255, 0, 255, 255)


class CueNullState(CueState):
    marker = 6
    label = '+'


class PrepState:
    marker = 10
    duration = 0.4
    label = '+'
    size = 48
    position = (0.5, 0.5)
    hold = False

    @staticmethod
    def next(state):
        return state.next_trial()

    @staticmethod
    def enter(state):
        trial = state.next_trial()
        PrepState.position = trial.position


class TrialState:
    duration = 3.1
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


class TrialStateCenter(TrialState):
    marker = 11
    position = (0.5, 0.5)


class TrialStateNE(TrialState):
    marker = 12
    position = (0.8, 0.8)


class TrialStateSE(TrialState):
    marker = 13
    position = (0.8, 0.2)


class TrialStateSW(TrialState):
    marker = 14
    position = (0.2, 0.2)


class TrialStateNW(TrialState):
    marker = 15
    position = (0.2, 0.8)


class FeedbackState:
    duration = 0.4
    size = 120
    hold = False

    @staticmethod
    def next(state):
        return RestState

    @staticmethod
    def enter(state):
        state.trial_count += 1
        state.stop_stim()


class FeedbackGoodState(FeedbackState):
    marker = 20
    label = '\u2714'


class FeedbackBadState(FeedbackState):
    marker = 21
    label = '\u2718'


class RestState:
    marker = 30
    duration = 0.4
    label = ''
    size = 48
    hold = False

    @staticmethod
    def next(state):
        if state.trial_count >= len(state.trial_sequence):
            state.block_count += 1
            return BlockEndState
        else:
            return state.next_cue()

    @staticmethod
    def enter(state):
        pass


class BlockStartState:
    duration = 2
    size = 48
    hold = False

    @staticmethod
    def next(state):
        return state.next_cue()

    @staticmethod
    def enter(state):
        state.trial_count = 0


class BlockStartOvertState(BlockStartState):
    marker = 31
    label = 'Overt'


class BlockStartCovertState(BlockStartState):
    marker = 32
    label = 'Covert'


class BlockStartGazeState(BlockStartState):
    marker = 33
    label = 'Overlapping'


class BlockEndState:
    marker = 34
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
    marker = 40
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
    marker = 41
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
