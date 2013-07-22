import pyglet
import array
import socket
import time

from unlock.util import TrialState, Trigger
from model import UnlockModel


class TimedSequenceStimuliManager(UnlockModel):
    """ Manages multiple timed, sequence-based stimuli. """
    def __init__(self, state, trigger):
        self.state = state
        self.stimuli = set([])
            
    def add_stimulus(self, stimulus):
        """
        add_stimulus(): adds a stimulus to the managed set
        """        
        self.stimuli.add(stimulus)
            
    def start(self):
        """
        start(): starts the stimuli
        """
        state.start()
        for stimulus in self.stimuli:
            stimulus.start()
            
    def pause(self):
        """
        pause(): pause the stimuli
        """
        for stimulus in self.stimuli:
            stimulus.stop()
            
    def stop(self):
        """
        stop(): stops the trial
        """
        self.state.stop()
        for stimulus in self.stimuli:
            stimulus.stop()
            
    def process_command(self, command):
        """
        process_command(): processes the next command
        """
        if self.state.stopped():
            log.debug("TimedSequenceStimuliManager.process_command: called when stopped")
            return
            
        if len(self.stimuli) < 1:
            log.debug("TimedSequenceStimuliManager.process_command: no stimulus available ")
            return
            
        ret = Trigger.Null
        state, change_value = self.state.update_state(command.delta)
        if state == RunState.running:
            sequence_start_trigger = False
            for stimulus in self.stimuli:
                sequence_start_trigger = stimulus.update(command)
            if sequence_start_trigger:
                ret = Trigger.Start
        elif change_value == TrialState.trial_expiry:
            self.pause()
        elif change_value == TrialState.rest_expiry:
            self.start()
            
        return ret
    
    @staticmethod
    def create(trial_state):
        state = TrialState()
            
            
class TimedSequenceStimulus(UnlockModel):
    """
    Emits a sequence of values at fixed time interval.
    time_state: manages the time (when to emit the next value)
    seq_state: manages the values to emit (on, on, off, on, off, on, off, off, etc..)
    """
    def __init__(self, time_state, seq_state):
        self.time_state = time_state
        self.seq_state = seq_state
        self.state_value = False
            
    def get_state(self):
        return state_value
            
    def start(self):
        self.seq_state.start()
        self.trial_time.begin_trial()
        self.first_pass = True
            
    def stop(self):
        """
        Stops stimulus 
        """
        self.state_value = False
            
    def process_command(self, command):
        """
        Updates the stimulus to the next state in the presentation
        sequence if the trial time is exceeded.
        
        A value of True is returned at the start of the sequence.
        """
        start_trigger = False
        self.time_state.update_trial_time(command.delta)
        if self.time_state.is_trial_complete() or self.first_pass:
            self.first_pass = False
            self.state = self.seq_state.state()
            if self.seq_state.is_start():
                start_trigger = True
            self.time_state.begin_trial()
            self.seq_state.step()
                
        return start_trigger
            
    @staticmethod
    def create(self, rate, sequence=(1,0), value_transformer_fn=lambda x: bool(x)):
        flick_rate = 0.5/rate
        time_state = TrialTimeState(flick_rate, 0)
        seq_state = SequenceState(sequence, value_transformer_fn)
        return TimedSequenceStimulus(flick_rate, time_state, seq_state)
            
         