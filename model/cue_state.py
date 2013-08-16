
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
        self.count = 0
        self.state = rest_state
        
    def __transition__(self, next_state):
        self.state.stop()
        next_state.last = self.state
        next_state.start()
        self.state = next_state
        return self.state.trigger
        
    def indicate_rest(self):
        return self.__transition__(self.rest_state)
            
    def rest_cue(self):
        self.count += 1
        if self.count == self.trials:
            return Trigger.Complete            
        return self.__transition__(self.cue_states[self.rand.randint(0, len(self.cue_states)-1)])
            
    def cue_indicate(self):
        return self.__transition__(self.indicate_state)
        
    def cue_rest(self):
        return self.__transition__(self.rest_state)
        
    def process_command(self, command):
        return self.state.process_command(command)
        
    def start(self):
        self.state.start()
        
    @staticmethod 
    def create_cue_indicate_rest(cue_states, rest_state, indicate_state, seed=42, trials=25):
        state_machine = RandomCueStateMachine(Random(seed), trials, cue_states, rest_state, indicate_state)
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_indicate
        rest_state.transition_fn = state_machine.rest_cue
        indicate_state.transition_fn = state_machine.indicate_rest
 #       rest_state.start()
        return state_machine
        
    @staticmethod
    def create_cue_rest(cue_states, rest_state, seed=42, trials=25):
        state_machine = RandomCueStateMachine(Random(seed), trials, cue_states, rest_state, None)
        for cue_state in cue_states:
            cue_state.transition_fn = state_machine.cue_rest
        rest_state.transition_fn = state_machine.rest_cue
#        rest_state.start()
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
        



class DynamicPositionCueState(CueState):
    def __init__(self, trigger, trial_time_state, screen_height, height, screen_width, width, radius = 1, transition_fn=None):
        super(DynamicPositionCueState, self).__init__(trigger, trial_time_state, transition_fn)
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.height = height
        self.width = width
        self.radius = radius
        self.x = self.screen_width / 2
        self.y = self.screen_height / 2
        
    def get_state(self):
        return self.x, self.y, self.state
 #
 #self.reset_state = CueState(self.state_id['reset'], TextDraw('+', self.text, viewport.controller.draw), self.trigger.send, reset_duration, None)
 #
 #       position_x = img.width // 2
 #       self.left_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
 #       self.left_indicator.drawer.screen = screen
 #       
 #       position_x = viewport.window.width - img.width // 2
 #       self.right_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
 #       
 #       position_x = viewport.window.width // 2
 #       position_y = viewport.window.height - img.height // 2
 #       self.up_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
 #       
 #       position_y = img.height // 2
 #       self.down_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
 #

   
    def start(self):
        #change position
        if self.last.trigger == Trigger.Up:
           self.x = self.screen_width / 2
           self.y = self.screen_height*self.radius - self.height / 2
        elif self.last.trigger == Trigger.Right:
            self.x = (self.screen_width*self.radius) - self.width / 2 
            self.y = self.screen_height / 2
        elif self.last.trigger == Trigger.Down:
            self.x = self.screen_width / 2
            self.y = self.height / 2 + ((self.screen_width/2) - (self.screen_width/2) * self.radius)
        elif self.last.trigger == Trigger.Left:
            self.x = self.width / 2 + ((self.screen_width/2) - (self.screen_width/2) * self.radius)
            self.y = self.screen_height / 2
            
        super(DynamicPositionCueState, self).start()
          
    @staticmethod
    def create(state_id, duration, screen_height, height, screen_width, width, radius=1):
        time_state = TrialTimeState(duration, 0)
        return DynamicPositionCueState(state_id, time_state, screen_height, height, screen_width, width, radius)
        
        
class TimedStimulusCueState(UnlockModel):
    def __init__(self, timed_stimulus):
        super(TimedStimulusCueState, self).__init__()
        self.timed_stimulus = timed_stimulus
        self.trigger = Trigger.Stop
        
    def start(self):
        assert self.transition_fn != None
        self.timed_stimulus.start()
        self.state = self.timed_stimulus.get_state()
        
    def stop(self):
        self.timed_stimulus.stop()
        self.state = None
        
    def process_command(self, command):
        assert self.transition_fn != None
        ret = Trigger.Null
        trigger_value = self.timed_stimulus.process_command(command)
        if trigger_value == Trigger.Stop:
            ret = self.transition_fn()
        else:
            self.state = self.timed_stimulus.get_state()
            
        return ret
        

class MultipleSequentialTimedStimuliCueState(UnlockModel):
    
    def __init__(self):
        super(MultipleSequentialTimedStimuliCueState, self).__init__()
        self.pos = -1
        self.stimuli = []
        self.trigger = None
        self.stimulus = None
    def add_stimulus(self, trigger, stimulus):
        self.stimuli.append((trigger, stimulus))

    def setup_next_stimulus(self):
        self.pos = (self.pos + 1) % len(self.stimuli)
        self.trigger, self.stimulus = self.stimuli[self.pos]
    
    def start(self):
        assert self.transition_fn != None
        assert len(self.stimuli) > 0
        self.setup_next_stimulus()
        self.stimulus.start()
        self.state = self.stimulus.get_state()
        
    def stop(self):
        assert len(self.stimuli) > 0
        self.stimulus.stop()
        self.state = None
        
    def process_command(self, command):
        assert self.transition_fn != None
        assert len(self.stimuli) > 0
        ret = Trigger.Null
        trigger_value = self.stimulus.process_command(command)
        if trigger_value == Trigger.Stop:
            ret = self.transition_fn()
        else:
            ret = trigger_value
            self.state = self.stimulus.get_state()            
        return ret
        
                               