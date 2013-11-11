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

from unlock.model.model import UnlockModel
from unlock.util import TrialState


class DiagnosticState(UnlockModel):
    """
    The diagnostic model supports two modes of operation: continuous and
     discrete. In the continuous mode, the stimuli is always flickering and the
     scope is always updating. In the discrete mode, the stimulus presents
     itself for a fixed amount of time, then the scope and/or decoder metrics
     are printed. The discrete mode trials are triggered by a selection event
     e.g. space bar press.
    """
    FrequencyUp = 1
    FrequencyDown = 2
    ChannelDown = 3
    ChannelUp = 4

    def __init__(self, scope, stimuli, frequencies=(10,), continuous=True):
        super(DiagnosticState, self).__init__()

        self.scope = scope
        self.stimuli = stimuli
        self.frequencies = frequencies
        self.cursor = 0
        self.continuous = continuous

    def process_command(self, command):
        if self.continuous:
            self.handle_continuous_command(command)
        else:
            self.handle_discrete_command(command)

    def handle_continuous_command(self, command):
        """
        For continuous usage, allow changes to the scope and stimuli
        frequencies at any event. The stimuli can also be started and stopped
        by the user.
        """
        if command.selection:
            if self.stimuli.model.state.is_stopped():
                self.stimuli.model.start()
            else:
                self.stimuli.model.stop()

        if command.decision is not None:
            self.handle_decision(command.decision)

    def handle_discrete_command(self, command):
        """
        For discrete usage, only allow changes when a trial is not underway.
        Handle the transition between trial and output.
        """
        if not self.stimuli.model.state.is_stopped():
            if self.stimuli.model.state.last_change == TrialState.TrialExpiry:
                self.stimuli.model.stop()
            else:
                return

        if command.selection:
            self.stimuli.model.start()

        if command.decision is not None:
            self.handle_decision(command.decision)

    def handle_decision(self, decision):
        if decision == DiagnosticState.FrequencyUp:
            self.cursor += 1
            if self.cursor >= len(self.frequencies):
                self.cursor = len(self.frequencies) - 1
            rate = 1 / (self.frequencies[self.cursor] * 2)
            self.stimuli.model.stimuli[0].time_state.set_duration(rate)
        elif decision == DiagnosticState.FrequencyDown:
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = 0
            rate = 1 / (self.frequencies[self.cursor] * 2)
            self.stimuli.model.stimuli[0].time_state.set_duration(rate)
        elif decision == DiagnosticState.ChannelDown:
            self.scope.model.change_display_channel(-1)
        elif decision == DiagnosticState.ChannelUp:
            self.scope.model.change_display_channel(1)