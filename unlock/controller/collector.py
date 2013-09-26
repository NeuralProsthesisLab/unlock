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

from unlock.model import TimedStimuli, TimedStimulus, OfflineData, RandomCueStateMachine, CueState, TimedStimulusCueState, MultipleSequentialTimedStimuliCueState, DynamicPositionCueState
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, PygletTextLabel, BellRingTextLabelDecorator, DynamicPositionPygletTextLabel
from unlock.util import TrialState, Trigger
from unlock.decode import RawInlineSignalReceiver

from .controller import Canvas, UnlockController

import inspect
import logging
import time
import os


class Collector(UnlockController):
    def __init__(self, window, views, canvas, command_receiver, cue_state, offline_data, timed_stimuli=None, standalone=True, icon="scope.png", name="Collector"):
        super(Collector, self).__init__(window, views, canvas)
        self.command_receiver = command_receiver
        self.cue_state = cue_state
        self.offline_data = offline_data
        self.timed_stimuli = timed_stimuli
        self.standalone = standalone
        self.name = name
        self.icon = icon
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(Collector)), 'resource', self.icon)
        self.logger = logging.getLogger(__name__)
        
    def poll_signal(self, delta):  
        self.logger.debug('Collector.poll signal delta = ', delta, ' time = ', time.time())
        command = self.command_receiver.next_command(delta)
        if self.timed_stimuli:
            sequence_trigger = self.timed_stimuli.process_command(command)
            if sequence_trigger != Trigger.Null:
                command.set_sequence_trigger(sequence_trigger)
                
        cue_trigger = self.cue_state.process_command(command)
        if cue_trigger != Trigger.Null:
            command.set_cue_trigger(cue_trigger)
            
        command.make_matrix()
        self.offline_data.process_command(command)
        if cue_trigger == Trigger.Complete:
            self.window.handle_stop_request()
        
        self.render()  
            
    def activate(self):
        self.cue_state.start()
        if self.timed_stimuli:
            self.timed_stimuli.start()
            
        self.offline_data.start()
        super(Collector, self).activate()
        
    def deactivate(self):
        self.command_receiver.stop()
        if self.timed_stimuli:
            self.timed_stimuli.stop()
            
        self.cue_state.stop()
        self.offline_data.stop()
        self.window.deactivate_controller()
        return self.standalone
      
    @staticmethod
    def create(mode, port, cue_duration, indicate_duration, rest_duration, channels, trials, seed, output):        
        pass
        
    @staticmethod
    def create_emg_collector(window, signal, timer, standalone=True, stimulation_duration=4.0, trials=25, cue_duration=1, rest_duration=1, indicate_duration=2, output_file='signal', seed=42, radius=1):
        canvas = Canvas.create(window.width, window.height)
        
        cues = [Trigger.Up, Trigger.Right, Trigger.Down, Trigger.Left]
        cue_states = []
        for cue in cues:
            cue_states.append(CueState.create(cue, cue_duration))
        rest_state = CueState.create(Trigger.Rest, rest_duration)
        
 #       h = canvas.height * radius
 #       w = canvas.width * radius
#        print "Radious, ", h,":", w, " height width = ", canvas.height, ":", canvas.width
        indicate_state = DynamicPositionCueState.create(Trigger.Indicate, indicate_duration, canvas.height, -1, canvas.width, -1, radius)
        
        cue_state = RandomCueStateMachine.create_cue_indicate_rest(cue_states, rest_state, indicate_state,seed=seed, trials=trials)
        
        up = PygletTextLabel(cue_state.cue_states[0], canvas, 'up', canvas.width / 2.0, canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0, canvas.height / 2.0)
        down = PygletTextLabel(cue_state.cue_states[2], canvas, 'down', canvas.width / 2.0, canvas.height / 2.0)
        left = PygletTextLabel(cue_state.cue_states[3], canvas, 'left', canvas.width / 2.0, canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)        
        
        indicate_text = DynamicPositionPygletTextLabel(cue_state.indicate_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
#        indicate = BellRingTextLabelDecorator(indicate_text)
        
        #print("Setting the indicate state height/width ", indicate_text.label.height, "/", indicate_text.label.width)
        indicate_state.height = 50#indicate_text.label.height
        indicate_state.width = 50#indicate_text.label.width
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        
        offline_data = OfflineData(output_file)
        
        return Collector(window, [up, right, down, left, rest, indicate_text], canvas, command_receiver, cue_state, offline_data, standalone=standalone)
        
    @staticmethod
    def create_msequence_collector(window, signal, timer, standalone=True, stimulation_duration=4.0, trials=2, cue_duration=1, rest_duration=2, indicate_duration=4, output_file='signal', seed=42):
        canvas = Canvas.create(window.width, window.height)        
        
        timed_stimuli = TimedStimuli.create(stimulation_duration)
        
        north_stimulus = TimedStimulus.create(30.0,  sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0))
        timed_stimuli.add_stimulus(north_stimulus)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(north_stimulus, canvas, SpritePositionComputer.North, width=200, height=200, xfreq=4, yfreq=4)
        
        east_stimulus = TimedStimulus.create(30.0, sequence=(0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0))
        timed_stimuli.add_stimulus(east_stimulus)            
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(east_stimulus, canvas, SpritePositionComputer.East, 90, width=200, height=200, xfreq=4, yfreq=4)
        
        south_stimulus = TimedStimulus.create(30.0, sequence=(0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1))
        timed_stimuli.add_stimulus(south_stimulus)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(south_stimulus, canvas, SpritePositionComputer.South, width=200, height=200, xfreq=4, yfreq=4)
        
        west_stimulus = TimedStimulus.create(30.0, sequence=(0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0))
        timed_stimuli.add_stimulus(west_stimulus)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(west_stimulus, canvas, SpritePositionComputer.West, 90, width=200, height=200, xfreq=4, yfreq=4)
        
        cues = [Trigger.Up, Trigger.Right, Trigger.Down, Trigger.Left]
        cue_states = []
        for cue in cues:
            cue_states.append(CueState.create(cue, cue_duration))
        rest_state = CueState.create(Trigger.Rest, rest_duration)
        indicate_state = CueState.create(Trigger.Indicate, indicate_duration)
        
        
        cue_state = RandomCueStateMachine.create_cue_indicate_rest(cue_states, rest_state, indicate_state,seed=seed, trials=trials)
        up = PygletTextLabel(cue_state.cue_states[0], canvas, 'up', canvas.width / 2.0, canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0, canvas.height / 2.0)
        down = PygletTextLabel(cue_state.cue_states[2], canvas, 'down', canvas.width / 2.0, canvas.height / 2.0)
        left = PygletTextLabel(cue_state.cue_states[3], canvas, 'left', canvas.width / 2.0, canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)        
        
        indicate_text = PygletTextLabel(cue_state.indicate_state, canvas, '', canvas.width / 2.0, canvas.height / 2.0)
        indicate = BellRingTextLabelDecorator(indicate_text)
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        
        offline_data = OfflineData(output_file)
        
        return Collector(window, [fs, fs1, fs2, fs3, up, right, down, left, rest, indicate], canvas, command_receiver, cue_state, offline_data, timed_stimuli, standalone)
        
    @staticmethod
    def create_single_centered_msequence_collector(window, signal, timer, standalone=True, stimulation_duration=4.0, trials=5, rest_duration=2, output_file='signal', seed=42):
        canvas = Canvas.create(window.width, window.height)        
        
        stimulus = TimedStimulus.create(30.0,  sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0), repeat_count=20)
        stimulated_cue = TimedStimulusCueState(stimulus)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(stimulated_cue, canvas, SpritePositionComputer.Center, width=200, height=200, xfreq=4, yfreq=4)
        
        cue_states = [stimulated_cue]
        rest_state = CueState.create(Trigger.Rest, rest_duration)
        
        cue_state = RandomCueStateMachine.create_cue_rest(cue_states, rest_state, seed=seed, trials=trials)
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        
        offline_data = OfflineData(output_file)
        
        return Collector(window, [fs, rest], canvas, command_receiver, cue_state, offline_data, None, standalone)
        
           
    @staticmethod
    def create_multi_centered_msequence_collector(window, signal, timer, standalone=True, stimulation_duration=4.0, trials=9, repeat_count=20, rest_duration=2, output_file='signal', seed=42, icon="rsz_analyzer.jpg"):
        canvas = Canvas.create(window.width, window.height)        
        # this should be a wrapper model that knows how to 
        north_stimulus = TimedStimulus.create(30.0,  sequence=(1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,0,1,1), repeat_count=repeat_count)
        east_stimulus = TimedStimulus.create(30.0,  sequence=(0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1), repeat_count=repeat_count)
        south_stimulus = TimedStimulus.create(30.0,  sequence=(0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0), repeat_count=repeat_count)
        west_stimulus = TimedStimulus.create(30.0,  sequence=(0,1,0,1,1,1,1,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1,1,0,1,0,0,1,1,0), repeat_count=repeat_count)

        stimulated_cue = MultipleSequentialTimedStimuliCueState()
        stimulated_cue.add_stimulus(Trigger.Up, north_stimulus)
        stimulated_cue.add_stimulus(Trigger.Right, east_stimulus)
        stimulated_cue.add_stimulus(Trigger.Down, south_stimulus)
        stimulated_cue.add_stimulus(Trigger.Left, west_stimulus)

        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(stimulated_cue, canvas, SpritePositionComputer.Center, width=200, height=200, xfreq=4, yfreq=4)
        
        #cues = [Trigger.Up, Trigger.Right, Trigger.Down, Trigger.Left]        
        
        cue_states = [stimulated_cue]
        rest_state = CueState.create(Trigger.Rest, rest_duration)
        
        cue_state = RandomCueStateMachine.create_cue_rest(cue_states, rest_state, seed=seed, trials=trials)
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        
        offline_data = OfflineData(output_file)
        
        return Collector(window, [fs, rest], canvas, command_receiver, cue_state, offline_data, None, standalone, icon, 'multi-single-msequence-collector') 
