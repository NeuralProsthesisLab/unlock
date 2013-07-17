import pyglet
import array
import socket
import time

from unlock.core import UnlockApplication
from unlock.util import TrialState, Trigger


class TimedSequenceStimuliManager(object):
    ''' This class manages multiple stimuli.  The reason for wrapping the stimuli is temporal precision.''' 
    def __init__(self, state, trigger):
        self.state = state
        self.trigger = trigger
        self.stimuli = []
        
    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)
        
    def start(self):
        for stimulus in self.stimuli:
            stimulus.start()
            
    def pause(self):
        for stimulus in self.stimuli:
            stimulus.stop()
            
    def stop(self):
        """
        stop(): Stop displaying the stimulus
        """
        self.state.stop()
        for stimulus in self.stimuli:
            stimulus.stop()
        self.trigger.send(Trigger.Stop)
            
    def process_command(self, command):
        if self.state.stopped():
            log.debug("TimedSequenceStimuliManager.process_command: called when stopped")
            return
            
        if len(self.stimuli) < 1:
            log.debug("TimedSequenceStimuliManager.process_command: no stimulus available ")
            return
            
        state, change_value = self.state.update_state(command.delta)
        if state == RunState.running:
            sequence_start_trigger = False
            for stimulus in self.stimuli:
                sequence_start_trigger = stimulus.update(command)
            if sequence_start_trigger:
                self.trigger.send(Trigger.Start)            
        elif change_value == TrialState.trial_expiry:
            self.pause()
        elif change_value == TrialState.rest_expiry:
            self.start()
            
            
class TimedSequenceStimulus(object):
    """
    Timed sequence stimulus emits a sequence of values managed by a TrialTimeState object.  For each trial the next
    value is emited to the view.  This can be used to control a flickering view.

    time_state: manages the time (when to toggle the pattern)
    seq_state: manages the pattern displayed (on, on, off, on, off, on, off, off, etc..)
    """
    def __init__(self, time_state, seq_state):
        self.time_state = time_state
        self.seq_state = seq_state
        self.state_value = False
    
    def state(self):
        return state_value
    
    def start(self):
        self.seq_state.start()
        self.trial_time.begin_trial()
        self.first_pass = True
        
    def stop(self):
        """
        Hides all stimulus images.
        """
        self.state_value = False
            
    def update(self, command):
        """
        Updates the stimulus to the next state in the presentation
        sequence if the elapsed trial time exceeds the next flicker time.
        
        A value of True is returned at the start of the state sequence.
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
            
         