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


class Markers:
    SEQUENCE = 1
    CUE_UP = 2
    CUE_DOWN = 3
    CUE_LEFT = 4
    CUE_RIGHT = 5
    CUE_A = 2
    CUE_B = 3
    CUE_NULL = 6
    ODDBALL_ON = 7
    ODDBALL_OFF = 8
    SPACEBAR_PRESS = 9
    PREP = 10
    TRIAL_FIXATION_CENTER = 11
    TRIAL_FIXATION_NORTHEAST = 12
    TRIAL_FIXATION_SOUTHEAST = 13
    TRIAL_FIXATION_SOUTHWEST = 14
    TRIAL_FIXATION_NORTHWEST = 15
    TRIAL_FIXATION_NORTH = 16
    TRIAL_FIXATION_SOUTH = 17
    TRIAL_FIXATION_WEST = 18
    TRIAL_FIXATION_EAST = 19
    FEEDBACK_GOOD = 20
    FEEDBACK_BAD = 21
    FEEDBACK_FIXATE = 22
    FEEDBACK_QUALITATIVE = 23
    FEEDBACK_INVALID_GAZE = 24
    REST = 30
    BLOCK_OVERT = 31
    BLOCK_COVERT = 32
    BLOCK_OVERLAPPED = 33
    BLOCK_END = 34
    EXPERIMENT_START = 40
    EXPERIMENT_END = 41


class ExperimentState(UnlockState):
    def __init__(self, mode, stim1, stim2, outlet, decoder, block_sequence, trials_per_block, demo=False):
        super(ExperimentState, self).__init__()
        self.mode = mode
        self.demo = demo
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
        self.block = None

        self.oddball_position = None
        self.oddball_offset = None
        self.oddball_color = None
        self.oddball_scale = 1
        self.oddball = (False, (0, 0), (0, 0, 0), 1)
        self.oddball_timer = None
        self.oddball_change = False

        self.invalid_gaze = False
        self.visual_angle_tolerance = 84  # 2 deg visual angle in pixels for 23" 1920x1080 LCD monitor

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

        self.feedback_scores = np.zeros(5)

    def get_feedback_score(self):
        return int(self.feedback_scores[self.cue])

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
        if self.invalid_gaze:
            return FeedbackInvalidGaze

        return FeedbackQualitativeState

    def get_oddball_state(self):
        if self.oddball_change:
            self.oddball_change = False
            return self.oddball

    def get_oddball(self):
        if self.trial_sequence[self.trial_count][2] == 1:
            t = 0.5 + 0.5*np.random.random()
            self.oddball_timer = TimerState(t)
            self.oddball_timer.begin_timer()

    def next_cue(self):
        self.cue = self.trial_sequence[self.trial_count][0]
        self.decoder.decoders[1].target_idx = self.cue
        return self.cues[self.cue]

    def next_trial(self):
        return self.fixations[self.trial_sequence[self.trial_count][1]]

    def next_block(self):
        self.block = self.block_sequence[self.block_count]
        self.decoder.decoders[1].set_block(self.block)
        block_state = self.blocks[self.block]
        n_trials = self.trials_per_block[self.block]
        if block_state is BlockStartGazeState:
            self.current_stim = self.stim2
            self.cues = [CueTileAState, CueTileBState, CueNullState]
            self.fixations = [TrialStateCenter, TrialStateNE, TrialStateSE, TrialStateSW, TrialStateNW]
            self.oddball_position = np.array([[60, 6], [-60, -6]])
            self.oddball_offset = np.array([[1014, 486], [1554, 810], [1554, 162], [366, 270], [366, 918]])
            self.oddball_color = ((0, 255, 0), (255, 0, 255))
            self.oddball_scale = 0.6
        else:
            self.current_stim = self.stim1
            self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState, CueNullState]
            if block_state is BlockStartOvertState:
                self.fixations = [TrialStateN, TrialStateS, TrialStateW, TrialStateE, TrialStateCenter]
            else:
                self.fixations = [TrialStateCenter]
            self.oddball_position = np.array([[960, 900], [960, 180], [600, 540], [1320, 540]])
            self.oddball_offset = np.zeros((4, 2))
            self.oddball_color = np.ones((4, 3))*255
            self.oddball_scale = 1

        n_targets = len(self.cues)
        if self.demo:
            n_targets = 5
        n_fixations = len(self.fixations)

        assert n_trials % n_targets == 0
        assert n_trials % n_fixations == 0
        if self.demo:
            cue_order = np.array([0, 1, 2, 0, 1])
        else:
            cue_order = np.repeat(np.arange(n_targets), int(n_trials / n_targets))
        if block_state is BlockStartOvertState:
            fixation_order = np.repeat(np.arange(n_fixations), int(n_trials / n_fixations))
        else:
            fixation_order = np.tile(np.arange(n_fixations), (int(n_trials / n_fixations),))
        oddball = np.zeros(len(cue_order))
        valid_cues = n_targets-1
        if self.demo and block_state is BlockStartGazeState:
            valid_cues = 2
        valid = np.where(cue_order < valid_cues)[0]
        if self.demo:
            oddball[valid[np.random.choice(len(valid), 1, replace=False)]] = 1
        elif block_state is BlockStartGazeState:
            oddball[valid[np.random.choice(len(valid), np.random.randint(2, 4), replace=False)]] = 1
        else:
            oddball[valid[np.random.choice(len(valid), np.random.randint(4, 7), replace=False)]] = 1
        order = np.vstack((cue_order, fixation_order, oddball))
        self.trial_sequence = np.random.permutation(order.T).astype(np.int32)
        return block_state

    def next_state(self):
        self.state = self.state.next(self)
        self.state.enter(self)
        self.outlet.push_sample([self.state.marker])
        self.timer = TimerState(self.state.duration)
        self.timer.begin_timer()
        self.state_change = True

    def update_feedback_scores(self, scores=None):
        if scores is not None:
            if self.demo:
                scores = np.random.random(5)
            if np.isnan(scores[self.cue]):
                return
            scores = 255 / (1 + np.exp(-5*(np.abs(scores) - 0.2)))
            self.feedback_scores[self.cue] = int(scores[self.cue])

    def check_gaze(self, gaze):
        # only check covert block trials
        if gaze is None or not self.blocks[self.block] is BlockStartCovertState or self.invalid_gaze:
            return

        self.invalid_gaze = (gaze[0] < 960 - self.visual_angle_tolerance or
                             gaze[0] > 960 + self.visual_angle_tolerance or
                             gaze[1] < 540 - self.visual_angle_tolerance or
                             gaze[1] > 540 + self.visual_angle_tolerance)

    def process_command(self, command):
        self.update_feedback_scores(scores=getattr(command, "decoder_scores", None))

        if self.state.hold:
            if command.selection:
                self.outlet.push_sample([Markers.SPACEBAR_PRESS])
                self.next_state()
        else:
            if command.selection:
                self.outlet.push_sample([Markers.SPACEBAR_PRESS])
            if command.delta is None:
                return
            self.timer.update_timer(command.delta)
            if self.timer.is_complete():
                self.next_state()
            if self.state.__base__ is TrialState:
                self.check_gaze(command.gaze)
                self.current_stim.process_command(command)
                if self.oddball_timer is not None:
                    self.oddball_timer.update_timer(command.delta)
                    if self.oddball_timer.is_complete():
                        if self.oddball[0]:
                            self.oddball_change = True
                            self.oddball = (False, (0, 0), (255, 255, 255), 1)
                            self.oddball_timer = None
                            self.outlet.push_sample([Markers.ODDBALL_OFF])
                        else:
                            fixation = self.trial_sequence[self.trial_count][1]
                            pos = self.oddball_position[self.cue] + self.oddball_offset[fixation]
                            self.oddball = (True, pos, self.oddball_color[self.cue], self.oddball_scale)
                            self.oddball_change = True
                            self.oddball_timer = TimerState(0.25)
                            self.oddball_timer.begin_timer()
                            self.outlet.push_sample([Markers.ODDBALL_ON])


class ExperimentTrainerState(ExperimentState):
    """
    build initial templates
     - run through each target individually for 12 seconds no feedback
     - create templates, determine optimal spatial filter
    reinforce templates
     - run through normally, with extended training times, providing continual feedback
     - stop after n trials with each target
    """
    def __init__(self, mode, stim1, stim2, outlet, decoder, block_sequence, trials_per_block, demo=False):
        super(ExperimentTrainerState, self).__init__(mode, stim1, stim2, outlet, decoder, block_sequence,
                                                     trials_per_block, demo=demo)

        self.feedback_scores = np.ones(5)*63
        self.feedback_target = np.ones(5)*63
        self.feedback_step = 0
        self.initial_phase = False
        if self.demo:
            TrialState.duration = 2.25
        else:
            TrialState.duration = 5.5

    def start_stim(self):
        self.current_stim.start()
        if self.initial_phase and self.cue != len(self.cues)-1:
            for i, stim in enumerate(self.current_stim.stimuli):
                if i == self.cue:
                    stim.state = False
                else:
                    stim.state = None

    def get_feedback(self):
        if self.initial_phase:
            return FeedbackFixateState
        else:
            return FeedbackQualitativeState

    def next_cue(self):
        self.cue = self.trial_sequence[self.trial_count][0]
        self.decoder.decoders[1].target_idx = self.cue
        return self.cues[self.cue]

    def next_block(self):
        self.block = self.block_sequence[self.block_count]
        block_state = self.blocks[self.block]
        n_trials = self.trials_per_block[self.block]

        if self.initial_phase:
            self.initial_phase = False
            self.decoder.decoders[1].updating = True
        else:
            self.initial_phase = True
            self.decoder.decoders[1].updating = False
            self.decoder.decoders[1].set_block(self.block)

        self.feedback_scores = np.ones(5)*63
        self.feedback_target = np.ones(5)*63
        self.feedback_step = 0

        if not self.initial_phase:
            n_trials *= 2

        if block_state is BlockStartGazeState:
            self.current_stim = self.stim2
            self.cues = [CueTileAState, CueTileBState, CueNullState]
            self.fixations = [TrialStateCenter]
            # if self.initial_phase:
            #     self.cues.append(CueNullState)
            # self.fixations = [TrialStateCenter, TrialStateNE, TrialStateSE, TrialStateSW, TrialStateNW]
        else:
            self.current_stim = self.stim1
            self.cues = [CueUpState, CueDownState, CueLeftState, CueRightState, CueNullState]
            # if self.initial_phase:
            #     self.cues.append(CueNullState)
            if block_state is BlockStartOvertState:
                self.fixations = [TrialStateN, TrialStateS, TrialStateW, TrialStateE, TrialStateCenter]
                # if self.initial_phase:
                #     self.fixations.append(TrialStateCenter)
            else:
                self.fixations = [TrialStateCenter]
        n_targets = len(self.cues)
        n_fixations = len(self.fixations)

        assert n_trials % n_targets == 0
        assert n_trials % n_fixations == 0
        cue_order = np.repeat(np.arange(n_targets), int(n_trials / n_targets))
        fixation_order = np.repeat(np.arange(n_fixations), int(n_trials / n_fixations))
        oddball = np.zeros(len(cue_order))
        order = np.vstack((cue_order, fixation_order, oddball))
        self.trial_sequence = np.random.permutation(order.T).astype(np.int32)
        return block_state

    def update_feedback_scores(self, scores=None):
        if scores is None:
            if self.cue is None or self.cue == len(self.feedback_scores):
                return
            score = self.feedback_scores[self.cue]
            if np.abs(self.feedback_target[self.cue] - score) > 5:
                score += self.feedback_step
                if score > 255:
                    score = 255
                if score < 0:
                    score = 0
                self.feedback_scores[self.cue] = score
        else:
            if np.isnan(scores[self.cue]):
                return
            if self.demo:
                scores = np.random.random(5)
            scores = 255 / (1 + np.exp(-5*(np.abs(scores) - 0.2)))
            self.feedback_target[self.cue] = int(scores[self.cue])
            # if self.demo:
            #     scores[self.cue] = 64
            # self.feedback_target[self.cue] += scores[self.cue]
            self.feedback_step = (self.feedback_target[self.cue] - self.feedback_scores[self.cue]) / 90.0

    def check_gaze(self, gaze):
        pass

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
    marker = Markers.CUE_UP
    label = '\u21e7'


class CueDownState(CueState):
    marker = Markers.CUE_DOWN
    label = '\u21e9'


class CueLeftState(CueState):
    marker = Markers.CUE_LEFT
    label = '\u21e6'


class CueRightState(CueState):
    marker = Markers.CUE_RIGHT
    label = '\u21e8'


class CueTileAState(CueState):
    marker = Markers.CUE_A
    label = '\u25a3'
    color = (0, 255, 0, 255)


class CueTileBState(CueState):
    marker = Markers.CUE_B
    label = '\u25a3'
    color = (255, 0, 255, 255)


class CueNullState(CueState):
    marker = Markers.CUE_NULL
    label = '+'


class PrepState:
    marker = Markers.PREP
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
    marker = Markers.TRIAL_FIXATION_CENTER
    position = (0.5, 0.5)


class TrialStateNE(TrialState):
    marker = Markers.TRIAL_FIXATION_NORTHEAST
    position = (0.8, 0.8)


class TrialStateSE(TrialState):
    marker = Markers.TRIAL_FIXATION_SOUTHEAST
    position = (0.8, 0.2)


class TrialStateSW(TrialState):
    marker = Markers.TRIAL_FIXATION_SOUTHWEST
    position = (0.2, 0.2)


class TrialStateNW(TrialState):
    marker = Markers.TRIAL_FIXATION_NORTHWEST
    position = (0.2, 0.8)


class TrialStateN(TrialState):
    marker = Markers.TRIAL_FIXATION_NORTH
    position = (0.5, 0.833)


class TrialStateS(TrialState):
    marker = Markers.TRIAL_FIXATION_SOUTH
    position = (0.5, 0.167)


class TrialStateW(TrialState):
    marker = Markers.TRIAL_FIXATION_WEST
    position = (0.3125, 0.5)


class TrialStateE(TrialState):
    marker = Markers.TRIAL_FIXATION_EAST
    position = (0.6875, 0.5)


class FeedbackState:
    duration = 0.5
    size = 120
    hold = False

    @staticmethod
    def next(state):
        return RestState

    @staticmethod
    def enter(state):
        if state.invalid_gaze:
            state.invalid_gaze = False
        else:
            state.trial_count += 1

        state.stop_stim()
        state.decoder.stop()


class FeedbackGoodState(FeedbackState):
    marker = Markers.FEEDBACK_GOOD
    label = '\u2714'


class FeedbackBadState(FeedbackState):
    marker = Markers.FEEDBACK_BAD
    label = '\u2718'


class FeedbackFixateState(FeedbackState):
    marker = Markers.FEEDBACK_FIXATE
    size = 48
    label = '+'


class FeedbackQualitativeState(FeedbackState):
    marker = Markers.FEEDBACK_QUALITATIVE
    label = ''


class FeedbackInvalidGaze(FeedbackState):
    marker = Markers.FEEDBACK_INVALID_GAZE
    label = '\u2718'
    color = (255, 0, 0, 255)


class RestState:
    marker = Markers.REST
    duration = 0.5
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
    marker = Markers.BLOCK_OVERT
    label = 'Overt'


class BlockStartCovertState(BlockStartState):
    marker = Markers.BLOCK_COVERT
    label = 'Covert'


class BlockStartGazeState(BlockStartState):
    marker = Markers.BLOCK_OVERLAPPED
    label = 'Overlapping'


class BlockEndState:
    marker = Markers.BLOCK_END
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
        state.decoder.decoders[1].save_templates()


class ExperimentStartState:
    marker = Markers.EXPERIMENT_START
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
    marker = Markers.EXPERIMENT_END
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
