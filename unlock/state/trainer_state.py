# Copyright (c) Byron Galbraith and Unlock contributors.
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
import numpy as np

from unlock.state.state import UnlockState, TrialState


class MsequenceTrainerState(UnlockState):
    NextStimulus = 1
    PrevStimulus = 2

    def __init__(self, stimuli, sequences, n_trials=None, trial_sequence=None):
        super(MsequenceTrainerState, self).__init__()
        self.stimuli = stimuli
        self.sequences = sequences
        self.cursor = 0
        self.n_trials = n_trials
        self.trial_count = 0
        if trial_sequence is None or trial_sequence == 'manual':
            self.trial_sequence = None
        elif trial_sequence == 'random':
            assert n_trials % len(self.sequences) == 0
            self.trial_sequence = np.random.permutation(np.repeat(
                np.arange(len(self.sequences)), n_trials / len(self.sequences))
            )
        else:
            self.trial_sequence = trial_sequence

    def trial_start(self):
        self.stimuli.start()

    def trial_stop(self):
        self.stimuli.stop()
        for stimulus in self.stimuli.stimuli:
            stimulus.state = None

    def process_command(self, command):
        if not self.stimuli.state.is_stopped():
            if self.trial_count == 0:
                # this is a hack to get around the current setup where the
                # stimuli starts immediately
                self.trial_stop()
            elif self.stimuli.state.last_change == TrialState.TrialExpiry:
                # there is an occasional delay apparently that can happen when
                # using actual devices which causes this state to be missed
                # i.e. it goes to rest, then the next rest state, resulting in
                # an Unchanged response, before this check happens. A better
                # method would preserve the value until it was queried.
                self.trial_stop()
            else:
                return

        if command.selection:
            self.trial_count += 1
            if self.trial_count <= self.n_trials:
                self.update_sequence()
                self.trial_start()

        if command.decision is not None:
            self.handle_decision(command.decision)

    def handle_decision(self, decision):
        if decision == MsequenceTrainerState.NextStimulus:
            self.cursor += 1
            if self.cursor >= len(self.sequences):
                self.cursor = 0
            self.update_sequence()
        elif decision == MsequenceTrainerState.PrevStimulus:
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = len(self.sequences) - 1
            self.update_sequence()

    def update_sequence(self):
        if self.trial_sequence is None:
            seq = self.sequences[self.cursor]
        else:
            seq = self.sequences[self.trial_sequence[self.trial_count-1]]
            print(self.trial_sequence[self.trial_count-1])
        self.stimuli.stimuli[0].seq_state.sequence = seq