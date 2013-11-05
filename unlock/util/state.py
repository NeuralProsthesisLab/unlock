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

import time


class RunState(object):
    Stopped = 0
    Running = 1
    Resting = 2

    def __init__(self):
        self.state = RunState.Stopped
        
    def run(self):
        self.state = RunState.Running
        
    def rest(self):
        self.state = RunState.Resting
        
    def stop(self):
        self.state = RunState.Stopped
        
    def is_running(self):
        return self.state == RunState.Running
        
    def is_resting(self):
        return self.state == RunState.Resting
        
    def is_stopped(self):
        return self.state == RunState.Stopped


class TimerState(object):
    """
    Keeps track of elapsed time
    """
    def __init__(self, duration):
        self.duration = float(duration)
        self.elapsed = 0
        self.last_time = -1

    def begin_timer(self):
        # TODO: smarter time adjustment strategy
        self.elapsed -= self.duration
        self.last_time = time.time()
        
    def update_timer(self, delta):
        self.elapsed += delta
        
    def is_complete(self):
        return self.elapsed >= self.duration

    def set_duration(self, duration):
        self.duration = float(duration)

        
class TrialState():
    Unchanged = 0
    TrialExpiry = 1
    RestExpiry = 2

    def __init__(self, trial_timer, rest_timer, run_state):
        self.trial_timer = trial_timer
        self.rest_timer = rest_timer
        self.run_state = run_state
        self.active_timer = self.trial_timer

        def state_change_fn():
            change_value = self.Unchanged
            if self.active_timer.is_complete():
                if self.run_state.is_running():
                    self.run_state.rest()
                    self.active_timer = self.rest_timer
                    change_value = self.TrialExpiry
                elif self.run_state.is_resting():
                    self.run_state.run()
                    self.active_timer = self.trial_timer
                    change_value = self.RestExpiry
                self.active_timer.begin_timer()
            return self.run_state.state, change_value
            
        self.update_state_table = state_change_fn
       
    def update_state(self, delta):
        self.active_timer.update_timer(delta)
        return self.update_state_table()
        
    def start(self):
        self.run_state.run()
        self.active_timer.begin_timer()
        
    def stop(self):
        self.run_state.stop()
        
    def is_stopped(self):
        return self.run_state.is_stopped()
        
    @staticmethod
    def create(stimuli_duration, rest_duration, run_state=RunState()):
        trial_timer = TimerState(stimuli_duration)
        rest_timer = TimerState(rest_duration)
        return TrialState(trial_timer, rest_timer, run_state)
        
        
class SequenceState(object):
    def __init__(self, sequence, value_transformer_fn=lambda x: x):
        self.sequence = sequence
        self.value_transformer_fn = value_transformer_fn
        
    def start(self):
        self.index = 0
       
    def step(self):
        self.index += 1        
        if self.index == len(self.sequence):
            self.start()
            
    def state(self):
        return self.value_transformer_fn(self.sequence[self.index])
            
    def is_start(self):
        if self.index == 0:
            return True
        else:
            return False
            
    def is_end(self):
        if self.index+1 == len(self.sequence):
            return True