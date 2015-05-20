"""
This is the hardcoded app setup for the cVEP BCI experiment trials. It is for the cued phase only. There
are three different paradigms: 4-choice overt, 2-choice covert, and 2-choice overlapped. In all three cases,
a template match based decoding approach will be used. These templates will be generated through an initial training
phase.

Training
 part 1 - initial template construction
   cue target. (2x each target, random order)
   target presented in isolation
   present target for 5.5 seconds (4 usable repetitions)
   no feedback
 part 2 - reinforcement
   cue target. (4x each target, random order)
   all targets active
   present target for 5.5 seconds (4 usable repetitions)
   qualitative feedback
 repeat for overt, covert, and overlapped

Testing
 cue target (10x each target, random order)
 all targets active
 include null target (attend only to fixation point)
 present target for 3.3 seconds (2 usable repetitions)
 occasionally present oddball stimulus for behavioral task
 qualitative feedback

Feedback
 training
   the MAD of each repetition is computed compared to the collected trials thus far
   the brightness of the feedback indicator is increased relative to this score
 testing
   the brightness of the feedback indicator is related to the decoder score for the intended target
   in null target case, brightness relative to "no decision" action

Behavioral Task
 to encourage and partially verify if the user is attending to the appropriate targets, occasionally present an
 oddball stimulus at the desired target location and have the user indicate that they saw it by pressing the space bar.

 about 10% of trials will have an oddball image
 the image will appear for 0.2s somewhere in the trial

"""
import numpy as np

from unlock.state import UnlockState, TimerState


class ExperimentState(UnlockState):
    def __init__(self, mode, stim1, stim2, outlet, decoder, block_sequence, trials_per_block):
        super(ExperimentState, self).__init__()
        self.mode = mode
        self.stim1 = stim1
        self.stim2 = stim2
        self.current_stim = self.stim1
        self.outlet = outlet
        self.decoder = decoder
        self.block_sequence = block_sequence
        self.n_blocks = len(block_sequence)
        self.blocks = [BlockStartOvertState, BlockStartCovertState, BlockStartGazeState]

        self.trials_per_block = trials_per_block

        self.trial_sequence = None
        self.cues = None
        self.fixations = None
        self.cue = None

        self.oddball_position = None
        self.oddball_offset = None
        self.oddball_color = None
        self.oddball_scale = 1
        self.oddball = (False, (0, 0), (0, 0, 0), 1)
        self.oddball_timer = None
        self.oddball_change = False

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

        self.feedback_scores = np.array([0, 0, 0, 0])
        self.feedback_target = np.array([0, 0, 0, 0])
        self.feedback_step = 0

    def get_feedback_score(self):
        return int(self.feedback_target[self.cue])

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

    def get_feedback(self):
        if self.cue == np.argmax(self.feedback_target):
            return FeedbackGoodState
        else:
            return FeedbackBadState

    def get_oddball_state(self):
        if self.oddball_change:
            self.oddball_change = False
            return self.oddball

    def get_oddball(self):
        if self.cue < len(self.cues)-1 and np.random.random() < 0.15:
            t = TrialState.duration / 2 + 0.5*np.random.random()
            self.oddball_timer = TimerState(t)
            self.oddball_timer.begin_timer()

    def next_cue(self):
        self.cue = self.trial_sequence[self.trial_count][0]
        return self.cues[self.cue]

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
            self.oddball_position = np.array([[60, 6], [-60, -6]])
            self.oddball_offset = np.array([[1014, 486], [1554, 810], [1554, 162], [366, 270], [366, 918]])
            self.oddball_color = ((0, 255, 0), (255, 0, 255))
            self.oddball_scale = 0.6
        else:
            self.current_stim = self.stim1
            self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState, CueNullState]
            if block is BlockStartOvertState:
                self.fixations = [TrialStateN, TrialStateS, TrialStateW, TrialStateE, TrialStateCenter]
            else:
                self.fixations = [TrialStateCenter]
            self.oddball_position = np.array([[960, 900], [960, 180], [600, 540], [1320, 540]])
            self.oddball_offset = np.zeros((4, 2))
            self.oddball_color = np.ones((4, 3))*255
            self.oddball_scale = 1

        n_targets = len(self.cues)
        n_fixations = len(self.fixations)

        assert n_trials % n_targets == 0
        assert n_trials % n_fixations == 0
        cue_order = np.repeat(np.arange(n_targets), int(n_trials / n_targets))
        if block is BlockStartOvertState:
            fixation_order = np.repeat(np.arange(n_fixations), int(n_trials / n_fixations))
        else:
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
        if hasattr(command, "decoder_scores"):
            scores = np.abs(command.decoder_scores)
            scores = 255 / (1 + np.exp(-10*(scores - 0.3)))
            scores = np.r_[scores, 0]
            # scores = 255 * np.exp(scores) / np.sum(np.exp(scores))
            # scores -= np.min(scores)
            # scores = scores / np.max(scores) * 255
            self.feedback_target[self.cue] = int(scores[self.cue])
            self.feedback_step = self.feedback_target[self.cue] - self.feedback_scores[self.cue] / 90.0
        elif (self.feedback_scores != self.feedback_target).all():
            self.feedback_scores[self.cue] += self.feedback_step

        if self.state.hold:
            if command.selection:
                self.next_state()
        else:
            self.timer.update_timer(command.delta)
            if self.timer.is_complete():
                self.next_state()
            if self.state.__base__ is TrialState:
                self.current_stim.process_command(command)
                if self.oddball_timer is not None:
                    self.oddball_timer.update_timer(command.delta)
                    if self.oddball_timer.is_complete():
                        if self.oddball[0]:
                            self.oddball_change = True
                            self.oddball = (False, (0, 0), (255, 255, 255), 1)
                            self.oddball_timer = None
                        else:
                            fixation = self.trial_sequence[self.trial_count][1]
                            pos = self.oddball_position[self.cue] + self.oddball_offset[fixation]
                            self.oddball = (True, pos, self.oddball_color[self.cue], self.oddball_scale)
                            self.oddball_change = True
                            self.oddball_timer = TimerState(0.2)
                            self.oddball_timer.begin_timer()



class ExperimentTrainerState(ExperimentState):
    """
    build initial templates
     - run through each target individually for 12 seconds no feedback
     - create templates, determine optimal spatial filter
    reinforce templates
     - run through normally, with extended training times, providing continual feedback
     - stop after n trials with each target
    """
    def __init__(self, mode, stim1, stim2, outlet, decoder, block_sequence, trials_per_block):
        super(ExperimentTrainerState, self).__init__(mode, stim1, stim2, outlet, decoder, block_sequence,
                                                     trials_per_block)
        self.initial_phase = False
        TrialState.duration = 5.5

    def start_stim(self):
        target_idx = self.trial_sequence[self.trial_count][0]
        self.current_stim.start()
        if self.initial_phase:
            for i, stim in enumerate(self.current_stim.stimuli):
                if i == target_idx:
                    stim.state = False
                else:
                    stim.state = None

    def get_feedback(self):
        return FeedbackBlankState

    def next_cue(self):
        self.cue = self.trial_sequence[self.trial_count][0]
        self.decoder.decoders[1].target_idx = self.cue
        return self.cues[self.cue]

    def next_block(self):
        if self.initial_phase:
            self.initial_phase = False
            self.decoder.decoders[1].save_templates()
            self.decoder.decoders[1].training = False
            self.decoder.decoders[1].updating = True
        else:
            self.initial_phase = True
            self.decoder.decoders[1].training = True
            self.decoder.decoders[1].updating = False
        block_idx = self.block_sequence[self.block_count]
        self.decoder.decoders[1].set_block(block_idx)
        block = self.blocks[block_idx]
        n_trials = self.trials_per_block[block_idx]
        # if not self.initial_phase:
        #     n_trials *= 3
        if block is BlockStartGazeState:
            self.current_stim = self.stim2
            self.cues = [CueTileAState, CueTileBState]
            self.fixations = [TrialStateCenter]
            # self.fixations = [TrialStateCenter, TrialStateNE, TrialStateSE, TrialStateSW, TrialStateNW]
        else:
            self.current_stim = self.stim1
            self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState]
            if block is BlockStartOvertState:
                self.fixations = [TrialStateN, TrialStateS, TrialStateW, TrialStateE]
            else:
                self.fixations = [TrialStateCenter]
        n_targets = len(self.cues)
        n_fixations = len(self.fixations)

        assert n_trials % n_targets == 0
        assert n_trials % n_fixations == 0
        cue_order = np.repeat(np.arange(n_targets), int(n_trials / n_targets))
        fixation_order = np.repeat(np.arange(n_fixations), int(n_trials / n_fixations))
        order = np.vstack((cue_order, fixation_order))
        self.trial_sequence = np.random.permutation(order.T)
        return block


class CueState:
    duration = 0.5
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
    duration = 0.5
    label = '+'
    size = 48
    position = (0.5, 0.5)
    hold = False

    @staticmethod
    def next(state):
        state.get_oddball()
        return state.next_trial()

    @staticmethod
    def enter(state):
        trial = state.next_trial()
        PrepState.position = trial.position


class TrialState:
    duration = 3.3
    label = '+'
    size = 48
    hold = False

    @staticmethod
    def next(state):
        return state.get_feedback()

    @staticmethod
    def enter(state):
        state.decoder.start()
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


class TrialStateN(TrialState):
    marker = 16
    position = (0.5, 0.833)


class TrialStateS(TrialState):
    marker = 17
    position = (0.5, 0.167)


class TrialStateW(TrialState):
    marker = 18
    position = (0.3125, 0.5)


class TrialStateE(TrialState):
    marker = 19
    position = (0.6875, 0.5)


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
        state.decoder.stop()


class FeedbackGoodState(FeedbackState):
    marker = 20
    label = '\u2714'


class FeedbackBadState(FeedbackState):
    marker = 21
    label = '\u2718'


class FeedbackBlankState(FeedbackState):
    marker = 22
    size = 48
    label = '+'


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
        state.decoder_scores = [63, 63, 63, 63]


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
        state.decoder.stop()


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
