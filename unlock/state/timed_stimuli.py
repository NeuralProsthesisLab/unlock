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
from unlock.state.state import UnlockState, TrialState, TimerState, RunState, SequenceState
from unlock.util import Trigger

import logging


class TimedStimuli(UnlockState):
    """ Manages multiple timed, sequence-based stimuli. """
    def __init__(self, state, stimuli=None):
        super(TimedStimuli, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.state = state
        if stimuli:
            self.stimuli = list(stimuli)
        else:
            self.stimuli = list()

        self.outlet = None
        self.seq_id = 1

    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)
            
    def start(self):
        self.state.start()
        for stimulus in self.stimuli:
            stimulus.start()
            
    def pause(self):
        for stimulus in self.stimuli:
            stimulus.stop()
            
    def stop(self):
        self.state.stop()
        for stimulus in self.stimuli:
            stimulus.stop()
            
    def process_command(self, command):
        if self.state.is_stopped():
           self.logger.debug("TimedSequenceStimuliManager.process_command: called when stopped")
           return
            
        if len(self.stimuli) < 1:
            self.logger.debug("TimedSequenceStimuliManager.process_command: no stimulus available ")
            return
            
        ret = Trigger.Null
        state, change_value = self.state.update_state(command.delta)
        self.logger.debug("state, change value ", state, change_value)
        if state == RunState.Running:
            sequence_start_trigger = False
            for stimulus in self.stimuli:
                response = stimulus.process_command(command)
                if response is Trigger.Start:
                    sequence_start_trigger = True
            if sequence_start_trigger:
                ret = Trigger.Start
                if self.outlet is not None:
                    self.outlet.push_sample([self.seq_id])
        elif change_value == TrialState.RestExpiry:
            self.start()
        elif change_value == TrialState.TrialExpiry:
            self.pause()
            
        return ret
            
    def get_state(self):
        raise NotImplementedError()


class SequentialTimedStimuli(UnlockState):
    """ Manages multiple timed, sequential and sequence-based stimuli. """
    def __init__(self, state):
        super(SequentialTimedStimuli, self).__init__()
        self.state = state
        self.stimuli = list()
        self.stimulus = None
        self.pos = 0
        self.logger = logging.getLogger(__name__)
            
    def add_stimulus(self, stimulus):
        if self.stimulus == None:
            self.stimulus = stimulus
        self.stimuli.append(stimulus)
            
    def start(self):
        self.state.start()
        self.stimulus.start()
            
    def pause(self):
        self.stimulus.stop()
        self.pos = (self.pos + 1) % len(self.stimuli)
#        print("PAUSED , pos = ", self.pos)
        self.stimulus = self.stimuli[self.pos]
            
    def stop(self):
        self.state.stop()
        self.stimulus.stop()
        self.stimulus = self.stimuli[0]
            
    def process_command(self, command):
        if self.state.is_stopped():
           self.logger.debug("TimedSequenceStimuliManager.process_command: called when stopped")
           return
            
        if len(self.stimuli) < 1:
            self.logger.debug("TimedSequenceStimuliManager.process_command: no stimulus available ")
            return
            
        ret = Trigger.Null
        state, change_value = self.state.update_state(command.delta)
        if state == RunState.Running:
            sequence_start_trigger = False
            sequence_start_trigger = self.stimulus.process_command(command)
            if sequence_start_trigger:
                ret = Trigger.Start
        elif change_value == TrialState.RestExpiry:
            self.start()
            
        elif change_value == TrialState.TrialExpiry:
            #print("Trial exiry... ")
            self.pause()
            
        return ret
            
    def get_state(self):
        raise NotImplementedError()


class TimedStimulus(UnlockState):
    """
    Emits a sequence of values at fixed time interval.
    time_state: manages the time (when to emit the next value)
    seq_state: manages the values to emit (on, on, off, on, off, on, off, off, etc..)
    """
    def __init__(self, time_state, seq_state, repeat_count=150):
        super(TimedStimulus, self).__init__()
        self.time_state = time_state
        self.seq_state = seq_state
        self.state = False
        self.count = 0
        self.repeat_count = 1
        self.logger = logging.getLogger(__name__)
            
    def get_state(self):
        return self.state
            
    def start(self):
        self.seq_state.start()
        self.state = self.seq_state.state()
        self.time_state.begin_timer()
        self.time_state.elapsed = 0  # force hard reset to 0

    def stop(self):
        self.state = False
            
    def process_command(self, command):
        """
        Updates the stimulus to the next state in the presentation
        sequence if the time state is exceeded.

        A value of Trigger.Start is returned at the start of the sequence.
        """
        trigger_value = Trigger.Null
        if self.state is None:
            return trigger_value

        self.time_state.update_timer(command.delta)
        if self.time_state.is_complete():
            self.state = self.seq_state.state()
            if self.seq_state.is_start():
                trigger_value = Trigger.Start
            elif self.seq_state.is_end():
                self.count += 1
                if self.count == self.repeat_count:
                    self.count = 0 
                    trigger_value = Trigger.Stop
                    command.stop = True
                else:
                    trigger_value = Trigger.Repeat
                    
            self.time_state.begin_timer()
            self.seq_state.step()
            
        return trigger_value
