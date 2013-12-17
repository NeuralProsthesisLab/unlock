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


class FacialEmgDiagnosticState(UnlockModel):
    Up = 'UP'
    Down = 'Down'
    Left = 'Left'
    Right = 'Right'
    Selection = 'Selection'
    def __init__(self, timer, classifier):
        super(FacialEmgDiagnosticState, self).__init__()
        self.timer = timer
        self.classifier = classifier
        self.text = ''
        
    def start(self):
        self.timer.begin_timer()
        self.classifier.reset()
        self.state = True
        self.text = 'Detecting'
        
    def stop(self):
        self.timer.reset()
        self.state = False
        
    def process_command(self, command):
        if command.keyboard_selection:
            self.start()
            return
                
        if not self.state:
            return
        
        self.timer.update_timer(command.delta)
        if command.decision is not None:
            self.handle_decision(command.decision)
        elif command.selection is not None:
            self.text = FacialEmgDiagnosticState.Selection
            
        if self.timer.is_complete():
            self.stop()
            
    def handle_decision(self, decision):
        if decision == FacialEMGDetector.UpDecision:
            self.text = FacialEmgDiagnosticState.Up
        elif decision == FacialEMGDetector.DownDecision:
            self.text = FacialEmgDiagnosticState.Down            
        elif decision == FacialEMGDetector.LeftDecision:
            self.text = FacialEmgDiagnosticState.Left
        elif decision == FacialEMGDetector.RightDecision:
            self.text = FacialEmgDiagnosticState.Right
            
            
class VepDiagnosticState(UnlockModel):
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

    def __init__(self, scope, stimuli, decoders, frequencies):
        super(VepDiagnosticState, self).__init__()
        self.scope = scope
        self.stimuli = stimuli
        self.frequencies = frequencies
        self.cursor = 0
        rate = 1 / (self.frequencies[self.cursor] * 2)
        self.stimuli.model.stimuli[0].time_state.set_duration(rate)
        self.decoders = decoders
        if decoders is None:
            self.decoders = list()
        for decoder in self.decoders:
            # this should be pushed into the decoder as an object reference
            # so changing it doesn't require a push-style update list this
            decoder.target_label = self.cursor

        self.trial_count = 0
        self.feedback_change = False
        self.feedback_results = list()

    def trial_start(self):
        print ("TRIAL START ")
        self.stimuli.model.start()
        for decoder in self.decoders:
            decoder.start()
        self.feedback_change = True
        self.feedback_results = list()

    def trial_stop(self):
        print ("TRIAL STop")
        self.stimuli.model.stop()
        for decoder in self.decoders:
            decoder.stop()
        self.feedback_change = True

    def process_command(self, command):
        raise Exception("Base class")
        return None

    def handle_decision(self, decision):
        print ("HANDLE DECISION")
        if decision == DiagnosticState.FrequencyUp:
            self.cursor += 1
            if self.cursor >= len(self.frequencies):
                self.cursor = len(self.frequencies) - 1
            rate = 1 / (self.frequencies[self.cursor] * 2)
            self.stimuli.model.stimuli[0].time_state.set_duration(rate)
            for decoder in self.decoders:
                decoder.target_label = self.cursor

        elif decision == DiagnosticState.FrequencyDown:
            self.cursor -= 1
            if self.cursor < 0:
                self.cursor = 0
            rate = 1 / (self.frequencies[self.cursor] * 2)
            self.stimuli.model.stimuli[0].time_state.set_duration(rate)
            for decoder in self.decoders:
                decoder.target_label = self.cursor

        elif decision == DiagnosticState.ChannelDown:
            if self.scope is not None:
                self.scope.model.change_display_channel(-1)
        elif decision == DiagnosticState.ChannelUp:
            if self.scope is not None:
                self.scope.model.change_display_channel(1)

    def update_decoders(self, command):
        print ("UPDATE DECODERS")
        for decoder in self.decoders:
            result = decoder.classify(command)
            if result is not None:
                self.feedback_results.append(result)

    def get_state(self):
        print("GET STATE")
        if self.feedback_change:
            text = ','.join(self.feedback_results)
            if text != '':
                text = '[%.1f Hz] - %s' % (self.frequencies[self.cursor], text)
            self.feedback_change = False
            return True, text
        else:
            return False, ''


class ContinuousVepDiagnosticState(VepDiagnosticState):
    def __init__(self, scope, stimuli, frequencies, decoders):
        super(ContinuousVepDiagnosticState, self).__init__(scope, stimuli, decoders, frequencies)

    def process_command(self, command):
        """
        For continuous usage, allow changes to the scope and stimuli
        frequencies at any event. The stimuli can also be started and stopped
        by the user.
        """
        if command.selection:
            if self.stimuli.model.state.is_stopped():
                self.trial_start()
            else:
                self.trial_stop()

        if command.decision is not None:
            self.handle_decision(command.decision)

        self.update_decoders(command)
        #return True
    

class DiscreteVepDiagnosticState(VepDiagnosticState):
    def __init__(self, scope, stimuli, decoders, frequencies):
        super(DiscreteVepDiagnosticState, self).__init__(scope, stimuli, decoders, frequencies)
        
    def process_command(self, command):
        """
        For discrete usage, only allow changes when a trial is not underway.
        Handle the transition between trial and output.
        """
        print("PROCESS COMMAND")
        if not self.stimuli.model.state.is_stopped():
            print("HACK STIMULLI state is stopped")
            if self.trial_count == 0:
                print(" trial count == 0")
                # this is a hack to get around the current setup where the
                # stimuli starts immediately
                self.trial_stop()
            elif self.stimuli.model.state.last_change == TrialState.TrialExpiry:
                print (" Trial expiry ")
                # there is an occasional delay apparently that can happen when
                # using actual devices which causes this state to be missed
                # i.e. it goes to rest, then the next rest state, resulting in
                # an Unchanged response, before this check happens. A better
                # method would preserve the value until it was queried.
                self.trial_stop()
                self.update_decoders(command)
            else:
                print (" ELSE UPDATE DECODERS ")
                self.update_decoders(command)
                return #True

        if command.selection:
            print ("Command selection ")
            self.trial_count += 1
            self.trial_start()

        if command.decision is not None:
            print("Command . decision not none")
            self.handle_decision(command.decision)
            
        #return True
    
    