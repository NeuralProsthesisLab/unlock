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

import numpy as np
import logging
import time

class UnlockState(object):
    def __init__(self, state=None):
        super(UnlockState, self).__init__()
        self.state = state
        self.running = False
        
    def start(self):
        self.running = True
        
    def stop(self):
        self.running = False
        
    def is_stopped(self):
        return self.running
        
    def get_state(self):
        return self.state
        
        
class AlternatingBinaryState(UnlockState):
    def __init__(self, hold_duration=300):
        self.hold_duration = hold_duration
        self.state = True
        self.count = 0
        
    def get_state(self):
        ret = self.state
        self.count += 1
        if self.count % self.hold_duration == 0:
            self.state = not self.state
        return ret
            
            
class OfflineData(UnlockState):
    def __init__(self, output_file_prefix, cache_size=1):
        super(OfflineData, self).__init__()
        self.output_file_prefix = output_file_prefix
        self.file_handle = None
        self.logger = logging.getLogger(__name__)
        self.cache = list(range(cache_size))
        self.cache_size = cache_size
        self.current = 0

    def cache(self, command):
        self.cache[self.current] = command.matrix
        self.current = 0 if (self.current % self.cache_size) == 0 else self.current + 1        
        
    def process_command(self, command):
        assert self.file_handle != None
        np.savetxt(self.file_handle, command.matrix, fmt='%d', delimiter='\t')
        
    def get_state(self):
        raise NotImplementedError()

    def start(self):
        assert self.file_handle == None
        self.file_handle = open("%s_%d.txt" % (self.output_file_prefix, time.time()), 'wb')
            
    def stop(self):
        assert self.file_handle != None
        self.file_handle.flush()
        self.file_handle.close()
        self.file_handle = None
        
        
class OfflineTrialData(OfflineData):
    def __init__(self, output_file_prefix, cache_size=1):
        super(OfflineTrialData, self).__init__(output_file_prefix, cache_size)
        self.commands = []
        
    def process_command(self, command):
        assert self.file_handle != None
        if not command.is_valid():
            return
        
        if command.decision is not None:
            for i in self.commands:        
                np.savetxt(self.file_handle, command.matrix, fmt='%d', delimiter='\t')
                self.cache(command)
                self.commands = []
        else:
            self.commands.append(command)
                
            
class NonBlockingOfflineData(UnlockState):
    def __init__(self):
        raise NotImplementedError()
        

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
    A timer based off the variable time deltas coming from the system.
    In the event the timer duration is small i.e. < 100ms, jitter in the delta
    value can cause problems. Keeping the residual time instead of a full
    reset has been shown to have better accuracy in this case.
    """
    def __init__(self, duration):
        self.duration = float(duration)
        self.reset = lambda t: 0
        if self.duration < 0.1:
            self.reset = lambda t: t - self.duration
        self.elapsed = 0
        self.last_time = -1

    def begin_timer(self):
        # TODO: smarter time adjustment strategy
        self.elapsed = self.reset(self.elapsed)
        self.last_time = time.time()
        
    def update_timer(self, delta):
        self.elapsed += delta
        
    def is_complete(self):
        return self.elapsed >= self.duration

    def set_duration(self, duration):
        self.duration = float(duration)
        
 
# XXX this can be refactored.  there is no need for a rest state.  this can be implemented such
#     that the trials are 'stacked'.  then rests can be stacked with trials abstractly.  this
#     would help to optimize cases that have no rest condition; currently a bunch of statements are
#     processed to handle that case.
class TrialState(object):
    Unchanged = 0
    TrialExpiry = 1
    RestExpiry = 2

    def __init__(self, trial_timer, rest_timer, run_state):
        super(TrialState, self).__init__()
        self.trial_timer = trial_timer
        self.rest_timer = rest_timer
        self.run_state = run_state
        self.active_timer = self.trial_timer
        
        self.state_change = False
        self.last_change = TrialState.Unchanged
        
        def state_change_fn():
            change_value = TrialState.Unchanged
            if self.active_timer.is_complete():
                if self.run_state.is_running():
                    self.run_state.rest()
                    self.active_timer = self.rest_timer
                    change_value = TrialState.TrialExpiry
                elif self.run_state.is_resting():
                    self.run_state.run()
                    self.active_timer = self.trial_timer
                    change_value = TrialState.RestExpiry
                self.active_timer.begin_timer()
            if change_value != TrialState.Unchanged:
                self.state_change = True
                self.last_change = change_value
            return self.run_state.state, change_value
            
        self.update_state_table = state_change_fn
       
    def update_state(self, delta):
        self.active_timer.update_timer(delta)
        return self.update_state_table()
        
    def start(self):
        self.active_timer = self.trial_timer
        self.last_change = TrialState.Unchanged
        self.run_state.run()
        self.active_timer.begin_timer()
        
    def stop(self):
        self.run_state.stop()
        
    def is_stopped(self):
        return self.run_state.is_stopped()
        
    def get_state(self):
        if self.state_change:
            self.state_change = False
            ret = self.last_change
            self.last_change = TrialState.Unchanged
            return ret
            
    @staticmethod
    def create(stimuli_duration, rest_duration, run_state=RunState()):
        trial_timer = TimerState(stimuli_duration)
        rest_timer = TimerState(rest_duration)
        return TrialState(trial_timer, rest_timer, run_state)
        
        
class SequenceState(object):
    def __init__(self, sequence, value_transformer_fn=lambda x: x):
        self.sequence = sequence
        self.value_transformer_fn = value_transformer_fn
        self.index = 0
        
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
           