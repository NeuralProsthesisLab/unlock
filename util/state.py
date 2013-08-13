
import time


class RunState(object):
    stopped = 0
    running = 1
    resting = 2
    def __init__(self):
        self.stop()
        
    def run(self):
        self.state = RunState.running
        
    def rest(self):
        self.state = RunState.resting
        
    def stop(self):
        self.state = RunState.stopped
        
    def is_running(self):
        return True if self.state == RunState.running else False
        
    def is_resting(self):
        return True if self.state == RunState.resting else False
        
    def is_stopped(self):
        return True if self.state == RunState.stopped else False
        
        
class TrialTimeState(object):
    def __init__(self, trial_duration=None, rest_duration=None):
        self.trial_duration = float(trial_duration)
        self.rest_duration = float(rest_duration)
        self.__set_period_duration__()
        self.trial_time = 0      
        self.last_time = -1

    def __set_period_duration__(self):
        self.period_duration = self.trial_duration + self.rest_duration
        
    def begin_trial(self):
        self.trial_time -= self.trial_duration
        self.last_time = time.time()
        
    def update_trial_time(self, delta):
        self.trial_time += delta
        
    def is_trial_complete(self):
        return True if self.trial_time >= self.trial_duration else False
        
    def is_rest_complete(self):
        return True if self.trial_time >= self.period_duration else False
        
    def set_trial_duration(self, duration):
        self.trial_duration = float(duration)
        self.__set_period_duration__()
        
    def set_rest_duration(self, duration):
        self.reset_duration = float(duration)
        self.__set_period_duration__()        
        
        
class TrialState():
    unchanged = 0
    trial_expiry = 1
    rest_expiry = 2
    def __init__(self, trial_time_state, trial_run_state):
        self.time_state = trial_time_state
        self.run_state = trial_run_state
        def state_change_fn():
            change_value = self.unchanged
            if self.run_state.is_running() and self.time_state.is_trial_complete():
                self.run_state.rest()
                change_value = self.trial_expiry
            elif self.run_state.is_resting() and self.time_state.is_rest_complete():
                self.run_state.run()
                self.time_state.begin_trial()
                change_value = self.rest_expiry                
            return self.run_state.state, change_value
            
        self.update_state_table = state_change_fn
       
    def update_state(self, delta):
        self.time_state.update_trial_time(delta)
        return self.update_state_table()
        
    def start(self):
        self.run_state.run()
        self.time_state.begin_trial()
        
    def stop(self):
        self.run_state.stop()
        
    def is_stopped(self):
        return self.run_state.is_stopped()
        
    @staticmethod
    def create(stimuli_duration, rest_duration, run_state=RunState()):
        return TrialState(TrialTimeState(stimuli_duration, rest_duration), run_state)
        
        
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
            
            