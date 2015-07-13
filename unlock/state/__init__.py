# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from unlock.state.state import *
from unlock.state.cue_state import *
from unlock.state.timed_stimuli import *
from unlock.state.grid_state import *
from unlock.state.fastpad_state import *
from unlock.state.scope_state import *
from unlock.state.diagnostic_state import *
from unlock.state.trainer_state import *
from unlock.state.robot_state import *


class UnlockStateFactory(object):
    def create_wall_clock_timed_stimulus(self, rate, sequence=(1,0), value_transformer_fn=lambda x: bool(x), repeat_count=1):
        flick_rate = 1.0/rate
        time_state = TimerState(flick_rate)
        seq_state = SequenceState(sequence, value_transformer_fn)
        return TimedStimulus(time_state, seq_state, repeat_count=repeat_count)

    def create_frame_counted_timed_stimulus(self, rate, sequence=(1,0), value_transformer_fn=lambda x: bool(x), repeat_count=150):
        time_state = FrameCountTimerState(rate)
        seq_state = SequenceState(sequence, value_transformer_fn)
        return TimedStimulus(time_state, seq_state, repeat_count=repeat_count)

    def create_sequential_timed_stimuli(self, stimuli_duration, rest_duration=0):
        # XXX this, and above, can be optimized in the case that rest_duration = 0
        trial_state = TrialState.create(stimuli_duration, rest_duration)
        return SequentialTimedStimuli(trial_state)

    def create_random_cue_indicate_rest(self, cue_states, rest_state, indicate_state, seed=42, trials=25):
        state_machine = CueStateMachine(Random(seed), trials, cue_states, rest_state, indicate_state)
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_indicate
        rest_state.transition_fn = state_machine.rest_cue
        indicate_state.transition_fn = state_machine.indicate_rest
 #       rest_state.start()
        return state_machine

    def create_sequential_cue_indicate_rest(self, cue_states, rest_state, indicate_state, trials=10):
        state_machine = CueStateMachine(None, trials, cue_states, rest_state, indicate_state)
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_indicate
        rest_state.transition_fn = state_machine.rest_cue
        indicate_state.transition_fn = state_machine.indicate_rest
        return state_machine

    def create_random_cue_rest(self, cue_states, rest_state, seed=42, trials=25):
        state_machine = CueStateMachine(Random(seed), trials, cue_states, rest_state, None)
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_rest
        rest_state.transition_fn = state_machine.rest_cue
#        rest_state.start()
        return state_machine

    def create_cue_state(self, state_id, duration):
        time_state = TimerState(duration)
        return CueState(state_id, time_state)

    def create_trial_state(self, stimuli_duration, rest_duration, run_state=RunState()):  # this reuses the same runstate object for all calls, should be fixed
        trial_timer = TimerState(stimuli_duration)
        rest_timer = TimerState(rest_duration)
        return TrialState(trial_timer, rest_timer, run_state)

    def create_dynamic_position_cue_state(self, state_id, duration, screen_height, height, screen_width, width, radius=1):
        time_state = TimerState(duration)
        return DynamicPositionCueState(state_id, time_state, screen_height, height, screen_width, width, radius)

    def create_fastpad(self):
        return FastPadState()

    def create_grid_state(self, controllers, icons):
        grid_state = ControllerGridState(controllers)
        return grid_state

    def create_grid_hierarchy(self, grid_radius):
        return HierarchyGridState(grid_radius)

    def create_robot_grid(self, grid_radius):
        return RobotGridState(grid_radius)

    def create_robot_controller(self, manual):
        return RobotManualDriveState(manual)

    def create_offline_data(self, output_file_name):
        offline_data = OfflineData(output_file_name)
        return offline_data

    def create_state_chain(self, *states):
        state_chain = UnlockStateChain(states)
        return state_chain

    def create_timed_stimuli(self, stimuli_duration=3.0, rest_duration=1.0, *stimuli):
        run_state = RunState()
        trial_state = self.create_trial_state(stimuli_duration, rest_duration, run_state)
        return TimedStimuli(trial_state, stimuli)

    def create_msequence_trainer(self, stimuli, sequences, n_trials,
                                 trial_sequence, position_sequence):
        trainer_state = MsequenceTrainerState(stimuli, sequences,
                                              n_trials, trial_sequence,
                                              position_sequence)
        return trainer_state

    def create_ssvep_trainer(self, stimuli, frequencies, n_trials,
                             trial_sequence, position_sequence):
        trainer_state = SsvepTrainerState(stimuli, frequencies,
                                          n_trials, trial_sequence,
                                          position_sequence)
        return trainer_state
