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
from unlock.controller import Canvas, UnlockControllerFragment, UnlockControllerChain

import numpy as np
import inspect
import logging
import time
import os


class FourwayCalibrationController(UnlockControllerFragment):
    def __init__(self, window, classifier, cue_state, views, batch):
        super(CalibrationController, self).__init__(cue_state, views, batch)
        self.cue_state = cue_state
        self.window = window
        self.classifier = classifier
        self.controllers = []
        self.last = None
        self.thresholds = {
            Trigger.Forward: [], Trigger.Back: [], Trigger.Left: [], Trigger.Right: [],
            Trigger.Select: []
        }
        
    def update_state(self, command):  
        if not command.is_valid():
            return
            
        cue_trigger = self.cue_state.process_command(command)
        if self.last != None and cue_trigger == Trigger.Indicate:
            # XXX - this is a bit weird.  if you look at Byron's femg.FacialEMGDetector, it just
            #       looks for electrode thresholds, so for calibration purposes it only makes
            #       sense to get a threshold for each electrode.
            #
            #       Seems like another way to do this would be to numerically incorporate all
            #       electrode values recorded during a given task.
            if self.last == Trigger.Left:
                lefts = self.thresholds[Trigger.Left]
                self.thresholds[Trigger.Left] = np.concatenate((lefts, command.data_matrix[:, 0]))                
            elif self.last == Trigger.Forward:
                bottoms = self.thresholds[Trigger.Forward]
                self.thresholds[Trigger.Forward] = np.concatenate((bottoms, command.data_matrix[:, 1]))                
            elif self.last == Trigger.Right:
                rights = self.thresholds[Trigger.Right]
                self.thresholds[Trigger.Right] = np.concatenate((rights, command.data_matrix[:, 2]))
            elif self.last == Trigger.Select:
                selects = self.thresholds[Trigger.Select]
                self.thresholds[Trigger.Select] = np.concatenate((selects, command.data_matrix[:, 3]))
                
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
        left =  np.mean(np.array(self.thresholds[Trigger.Left]))
        bottom = np.mean(np.array(self.thresholds[Trigger.Forward]))
        right =  np.mean(np.array(self.thresholds[Trigger.Right]))
        select = np.mean(np.array(self.thresholds[Trigger.Select]))
        self.classifier.thresholds = np.array([left, bottom, right, select])
        
    def keyboard_input(self, command):
        pass
    
  