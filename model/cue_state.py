

class RandomCueStateMachine(UnlockModel):
    def __init__(self, rand, trials, cue_states, rest_state, indicator_state):
        super(UnlockModel, self).__init__()
        self.cue_states = cue_states
        self.rest_state = rest_state
        self.indicator_state = indicator_state
        self.rand = rand
        self.trials = trials
        
    def __transition__(self, next_state):
        self.state.stop()
        next_state.last = self.state
        next_state.start()
        self.state = next_state
        
    def indicator_state(self):
        self.__transition__(self.rest_state)
        
    def rest_state(self):
        self.__transition__(self.cue_states[self.rand.randint(0, len(self.cue_states)-1)])
        
    def cue_state(self):
        self.__transition__(self.indicator_state)
        
    def process_command(self, command):
        self.count += 1
        self.state = self.state.process_command(command)
        
    @staticmethod
    def create(trials, cues, cue_duration, rest_duration, indication_duration, seed=42):
        cue_states = []
        for cue in cues:
            cue_states.append(CueState.create(cue, cue_duration))
        rest_state = CueState.create(CueState.Rest, rest_duration)
        indicator_state = CueState.create(CueState.Indicator, indication_duration)
        state_machine = RandomCueStateMachine(random.Random(seed), trials, cue_states, rest_state, indicator_state)
        for cue_state in cues_states:
            cue_state.transition_fn = state_machine.cue_state
        rest_state.transition_fn = state_machine.rest_state
        indicator_state.transition_fn = state_machine.indicator_state
        
        rest_state.start()
        
        
class CueState(UnlockModel):
    Rest = 0
    Indicator = 1
    Left = 2
    Right = 3
    Up = 4
    Down = 5
    def __init__(self, state_id, trial_time_state, transition_fn=None):
        super(TimedState, self).__init__()
        self.state = False
        self.state_id = state_id
        self.trial_time_state = trial_time_state
        self.transition_fn = transition_fn
        
    def get_state(self):
        return self.state

    def start(self):
        assert self.transition_fn != None        
        self.trial_state.begin_trial()
        self.state = True
        
    def stop(self):
        self.state = False
        
    def process_command(self, command):
        assert self.transition_fn != None
        self.trial_state.update_trial_time(command.delta)
        if self.trial_state.is_trial_complete():
            self.transition_fn()
            
    @staticmethod
    def create(state_id, duration):
        time_state = TrialTimeState(duration, 0)
        return CueState(state_id, time_state)
        
       
