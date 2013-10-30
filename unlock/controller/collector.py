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

from unlock.model import OfflineData, CueStateMachine, CueState, DynamicPositionCueState
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, PygletTextLabel, BellRingTextLabelDecorator, DynamicPositionPygletTextLabel
from unlock.util import TrialState, Trigger
from unlock.decode import RawInlineSignalReceiver

from unlock.controller import Canvas, UnlockControllerFragment, UnlockControllerChain

import inspect
import logging
import time
import os

class Collector(UnlockControllerFragment):
    def __init__(self, window, cue_state, offline_data, views, batch, standalone=True):
        super(Collector, self).__init__(None, views, batch, standalone=False)
        self.cue_state = cue_state
        self.offline_data = offline_data
        self.window = window
        
    def update_state(self, command):  
        cue_trigger = self.cue_state.process_command(command)
        if cue_trigger != Trigger.Null:
            command.set_cue_trigger(cue_trigger)
   
        command.make_matrix()
        self.offline_data.process_command(command)
        if cue_trigger == Trigger.Complete:
            self.window.deactivate_controller()

    def keyboard_input(self, command):
        pass

    def activate(self):
        self.cue_state.start()
        self.offline_data.start()
        
    def deactivate(self):
        self.cue_state.stop()
        self.offline_data.stop()
        return self.standalone
      
    @staticmethod
    def create_eye_based_emg_collector(window, decoder, stimuli=None, trials=10, cue_duration=.5,
                         rest_duration=1, indicate_duration=1, output_file='collector', standalone=False):
        canvas = Canvas.create(window.width, window.height)
        cues = [Trigger.Left, Trigger.Right, Trigger.Up, Trigger.Down, Trigger.Select]
        cue_states = []
        for cue in cues:  
            cue_states.append(CueState.create(cue, cue_duration))
                              
        rest_state = CueState.create(Trigger.Rest, rest_duration)

        indicate_state = DynamicPositionCueState.create(Trigger.Indicate, indicate_duration, canvas.height, canvas.height/8,
                                              canvas.width, canvas.width/8)
        
        cue_state = CueStateMachine.create_sequential_cue_indicate_rest(cue_states, rest_state,
                                                                        indicate_state,trials=trials)
        
        left = PygletTextLabel(cue_state.cue_states[0], canvas, 'left', canvas.width / 2.0,
                               canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0,
                                canvas.height / 2.0)
        forward = PygletTextLabel(cue_state.cue_states[2], canvas, 'up', canvas.width / 2.0,
                                  canvas.height / 2.0)
        back = PygletTextLabel(cue_state.cue_states[3], canvas, 'down', canvas.width / 2.0,
                               canvas.height / 2.0)
        select = PygletTextLabel(cue_state.cue_states[4], canvas, 'select', canvas.width / 2.0,
                                 canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)
        
        indicate_text = DynamicPositionPygletTextLabel(cue_state.indicate_state, canvas, '+',
                                                       canvas.width / 2.0, canvas.height / 2.0)
        
        offline_data = OfflineData(output_file)
        collector = Collector(window, cue_state, offline_data, [left, right, forward, back, select, rest, indicate_text],
                              canvas.batch, standalone=standalone)
        view_chain = collector.views
        
        command_receiver = RawInlineSignalReceiver(decoder.signal, decoder.timer)
        
        controller_chain = UnlockControllerChain(window, command_receiver,
                                                 [collector] , 'Collector', 'collector.png',
                                                 standalone=standalone)
        return controller_chain
            
    @staticmethod
    def create_mouth_based_emg_collector(window, decoder, stimuli=None, trials=10, cue_duration=.5,
                         rest_duration=1, indicate_duration=1, output_file='collector', standalone=False):
        canvas = Canvas.create(window.width, window.height)
        cues = [Trigger.Left, Trigger.Right, Trigger.Forward, Trigger.Back, Trigger.Select]
        cue_states = []
        for cue in cues:  
            cue_states.append(CueState.create(cue, cue_duration))
                              
        rest_state = CueState.create(Trigger.Rest, rest_duration)

        indicate_state = CueState.create(Trigger.Indicate, indicate_duration)
        
        cue_state = CueStateMachine.create_sequential_cue_indicate_rest(cue_states, rest_state,
                                                                        indicate_state,trials=trials)
        
        left = PygletTextLabel(cue_state.cue_states[0], canvas, 'left', canvas.width / 2.0,
                               canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0,
                                canvas.height / 2.0)
        forward = PygletTextLabel(cue_state.cue_states[2], canvas, 'forward', canvas.width / 2.0,
                                  canvas.height / 2.0)
        back = PygletTextLabel(cue_state.cue_states[3], canvas, 'back', canvas.width / 2.0,
                               canvas.height / 2.0)
        select = PygletTextLabel(cue_state.cue_states[4], canvas, 'select', canvas.width / 2.0,
                                 canvas.height / 2.0)
        
        rest = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
#        rest = BellRingTextLabelDecorator(rest_text)
        
        indicate_text = BellRingTextLabelDecorator(PygletTextLabel(cue_state.indicate_state, canvas, '',
                                       canvas.width / 2.0, canvas.height / 2.0))
        
        offline_data = OfflineData(output_file)
        collector = Collector(window, cue_state, offline_data, [left, right, forward, back, select, rest, indicate_text],
                              canvas.batch, standalone=standalone)
        view_chain = collector.views
        
        command_receiver = RawInlineSignalReceiver(decoder.signal, decoder.timer)
        
        controller_chain = UnlockControllerChain(window, command_receiver,
                                                 [collector] , 'Collector', 'collector.png',
                                                 standalone=standalone)
        return controller_chain
            
            