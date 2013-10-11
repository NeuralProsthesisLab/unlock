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

from unlock.model import CueStateMachine, CueState
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, PygletTextLabel, BellRingTextLabelDecorator
from unlock.util import TrialState, Trigger
#from unlock.decode import RawInlineSignalReceiver

from .controller import Canvas, UnlockControllerFragment, UnlockControllerChain

import inspect
import logging
import time
import os


class Calibrate(UnlockControllerFragment):
    def __init__(self, window, cue_state_model, views, batch, stimuli, standalone=False):
        super(Calibrate, self).__init__(cue_state_model, views, batch, standalone=False)
        self.cue_state = cue_state_model
        self.stimuli = stimuli
        self.window = window
        self.controllers = []
        self.last = None
        self.thresholds = { Trigger.Left: [], Trigger.Right: [], Trigger.Forward: [],
            Trigger.Back: [], Trigger.Select: []}
        
    def update_state(self, command):  
        if not command.is_valid():
            return

        cue_trigger = self.cue_state.process_command(command)
        if self.last != None and cue_trigger == Trigger.Indicate:
            self.thresholds[self.last].append(command.rms_data)
            
        if cue_trigger == Trigger.Left:
            self.last = Trigger.Left
        elif cue_trigger == Trigger.Right:
            self.last = Trigger.Right
        elif cue_trigger == Trigger.Forward:
            self.last = Trigger.Forward            
        elif cue_trigger == Trigger.Back:
            self.last = Trigger.Back            
        elif cue_trigger == Trigger.Select:
            self.last = Trigger.Select
        elif cue_trigger == Trigger.Indicate:
            self.last = None
            
        if cue_trigger == Trigger.Complete:
            self.calibrate()
            self.window.deactivate_controller()
            
    def calibrate(self):
        for k, v in self.thresholds.items():
            print(Trigger.tostring(k), v)
            
    def keyboard_input(self, command):
        pass
    
    @staticmethod
    def create_smg_calibrator(window, signal, timer, stimuli=None, trials=4, cue_duration=.5,
                              rest_duration=1, indicate_duration=1, standalone=False):
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
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
        
        
        indicate_text = PygletTextLabel(cue_state.indicate_state, canvas, '',
                                                       canvas.width / 2.0, canvas.height / 2.0)
        indicate = BellRingTextLabelDecorator(indicate_text)        
        
        calibrate = Calibrate(window, cue_state, [left, right, forward, back, select, rest_text, indicate],
                              canvas.batch, stimuli, standalone=standalone)
        view_chain = stimuli.views + calibrate.views
        controller_chain = UnlockControllerChain(window, stimuli.command_receiver,
                                                 [stimuli, calibrate] , 'Calibrate', 'scope.png',
                                                 standalone=standalone)
        return calibrate, controller_chain
