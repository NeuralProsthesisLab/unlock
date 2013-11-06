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


class DiagnosticState(UnlockModel):
    FrequencyUp = 1
    FrequencyDown = 2
    ChannelDown = 3
    ChannelUp = 4

    def __init__(self, scope, stimulus, frequencies=(10,)):
        super(DiagnosticState, self).__init__()

        self.scope = scope
        self.stimulus = stimulus
        self.frequencies = frequencies
        self.cursor = 0

    def process_command(self, command):
        if command.decision == DiagnosticState.FrequencyUp:
            self.cursor += 1
            if self.cursor >= len(self.frequencies):
                self.cursor = len(self.frequencies) - 1
            rate = 1 / self.frequencies[self.cursor]
            self.stimulus.model.time_state.set_trial_duration(rate)
        elif command.decision == DiagnosticState.FrequencyDown:
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = 0
            rate = 1 / self.frequencies[self.cursor]
            self.stimulus.model.time_state.set_trial_duration(rate)
        elif command.decision == DiagnosticState.ChannelDown:
            self.scope.model.change_display_channel(-1)
        elif command.decision == DiagnosticState.ChannelUp:
            self.scope.model.change_display_channel(1)