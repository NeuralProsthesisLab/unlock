
from unlock.util import TrialState, TrialTimeState, RunState, Trigger, SequenceState
from model import UnlockModel

import logging


class TimedStimuli(UnlockModel):
    """ Manages multiple timed, sequence-based stimuli. """
    def __init__(self, state):
        super(UnlockModel, self).__init__()
        self.state = state
        self.stimuli = set([])
        self.logger = logging.getLogger(__name__)
        
    def add_stimulus(self, stimulus):
        self.stimuli.add(stimulus)
            
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
        if state == RunState.running:
            sequence_start_trigger = False
            for stimulus in self.stimuli:
                sequence_start_trigger = stimulus.process_command(command)
            if sequence_start_trigger:
                ret = Trigger.Start
        elif change_value == TrialState.rest_expiry:
            self.start()
        elif change_value == TrialState.trial_expiry:
            self.pause()
            
        return ret
    
    def get_state(self):
        raise NotImplementedError()
    
    @staticmethod
    def create(stimuli_duration):
        trial_state = TrialState.create(stimuli_duration, 0)
        return TimedStimuli(trial_state)
            
            
class TimedStimulus(UnlockModel):
    """
    Emits a sequence of values at fixed time interval.
    time_state: manages the time (when to emit the next value)
    seq_state: manages the values to emit (on, on, off, on, off, on, off, off, etc..)
    """
    def __init__(self, time_state, seq_state):
        super(TimedStimulus, self).__init__()
        self.time_state = time_state
        self.seq_state = seq_state
        self.state = False
        self.logger = logging.getLogger(__name__)
            
    def get_state(self):
        return self.state
            
    def start(self):
        self.seq_state.start()
        self.state = self.seq_state.state()
        self.time_state.begin_trial()
            
            
    def stop(self):
        self.state = False
            
    def process_command(self, command):
        """
        Updates the stimulus to the next state in the presentation
        sequence if the trial time is exceeded.
        
        A value of Trigger.Start is returned at the start of the sequence.
        """
        trigger_value = Trigger.Null
        self.time_state.update_trial_time(command.delta)
        if self.time_state.is_trial_complete():
            self.state = self.seq_state.state()
            if self.seq_state.is_start():
                start_trigger = Trigger.Start
            elif self.seq_state.is_end():
                trigger_value = Trigger.Stop
            self.time_state.begin_trial()
            self.seq_state.step()
            self.logger.debug("TimedStimulus trial complete; next state = ", self.state)
        return trigger_value
            
    @staticmethod
    def create(rate, sequence=(1,0), value_transformer_fn=lambda x: bool(x)):
        flick_rate = 0.5/rate
        time_state = TrialTimeState(flick_rate, 0)
        seq_state = SequenceState(sequence, value_transformer_fn)
        return TimedStimulus(time_state, seq_state)
            
         