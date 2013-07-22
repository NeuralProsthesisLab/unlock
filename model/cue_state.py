from unlock.util import TrialTimeState, Trigger
from model import UnlockModel
from random import Random

class RandomCueStateMachine(UnlockModel):
    def __init__(self, rand, trials, cue_states, rest_state, indicate_state):
        super(UnlockModel, self).__init__()
        self.cue_states = cue_states
        self.rest_state = rest_state
        self.indicate_state = indicate_state
        self.rand = rand
        self.trials = trials
        self.state = rest_state
        
    def __transition__(self, next_state):
        self.state.stop()
        next_state.last = self.state
        next_state.start()
        self.state = next_state
        return self.state.trigger
        
    def indicate_transition(self):
        return self.__transition__(self.rest_state)
        
    def rest_transition(self):
        return self.__transition__(self.cue_states[self.rand.randint(0, len(self.cue_states)-1)])
        
    def cue_transition(self):
        return self.__transition__(self.indicate_state)
        
    def process_command(self, command):
        return self.state.process_command(command)
        
    def start(self):
        self.state.start()
        
    @staticmethod
    def create(trials, cues, cue_duration, rest_duration, indicate_duration, seed=42):
        cue_states = []
        for cue in cues:
            cue_states.append(CueState.create(cue, cue_duration))
            
        rest_state = CueState.create(Trigger.Rest, rest_duration)
        indicate_state = CueState.create(Trigger.Indicate, indicate_duration)
        state_machine = RandomCueStateMachine(Random(seed), trials, cue_states, rest_state, indicate_state)
        
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_transition
            
        rest_state.transition_fn = state_machine.rest_transition
        indicate_state.transition_fn = state_machine.indicate_transition
        rest_state.start()
        return state_machine
        
        
class CueState(UnlockModel):
    def __init__(self, trigger, trial_time_state, transition_fn=None):
        super(CueState, self).__init__()
        self.state = False
        self.trigger = trigger
        self.trial_time_state = trial_time_state
        self.transition_fn = transition_fn
        
    def get_state(self):
        return self.state
        
    def start(self):
        assert self.transition_fn != None        
        self.trial_time_state.begin_trial()
        self.state = True
        
    def stop(self):
        self.state = False
        
    def process_command(self, command):
        assert self.transition_fn != None
        ret = Trigger.Null
        self.trial_time_state.update_trial_time(command.delta)
        if self.trial_time_state.is_trial_complete():
            ret = self.transition_fn()
            
        return ret
            
    @staticmethod
    def create(state_id, duration):
        time_state = TrialTimeState(duration, 0)
        return CueState(state_id, time_state)
        
       