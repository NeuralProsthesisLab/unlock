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
import json
import pickle
import logging
import pyglet
import time
import numpy as np


class Command(object):
    def __init__(self, delta=None, decision=None, selection=None, data=None, json=False):
        super(Command, self).__init__()        
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.predicted_decision = None
        self.predicted_decision_confidence = None
        self.data = data
        self.json = json
        self.ready = True
        
    def is_valid(self):
        return False
        
    def set_ready_value(self, ready_value):
        self.ready = ready_value
        
    def is_ready(self):
        return self.ready
        
    @staticmethod
    def serialize(command):
        if command.json:
            ret = json.dumps(command)
        else:
            ret = pickle.dumps(command)
        return ret
           
    @staticmethod
    def deserialize(serialized_command, json=False):
        if json:
            ret = json.loads(serialized_command)
        else:
            ret = pickle.loads(serialized_command)
        return ret
            
            
class PygletKeyboardCommand(Command):
    def __init__(self, symbol, modifiers):
        super(PygletKeyboardCommand, self).__init__()
        self.stop = False
        labels = [ord(c) for c in 'abcdefghijklmnopqrstuvwxyz_12345']
        if symbol == pyglet.window.key.UP:
            self.decision = 1
        elif symbol == pyglet.window.key.DOWN:
            self.decision = 2
        elif symbol == pyglet.window.key.LEFT:
            self.decision = 3 
        elif symbol == pyglet.window.key.RIGHT:
            self.decision = 4
        elif symbol == pyglet.window.key.SPACE:
            self.selection = 1
        elif symbol == pyglet.window.key.ESCAPE:
            self.stop = True
        elif symbol in labels:
            self.decision = labels.index(symbol) + 1
            
    def is_valid(self):
        return False
            
            
class RawSignalCommand(Command):
    TriggerCount = 4
    def __init__(self, delta, raw_data_vector, samples, channels, timer):
        super(RawSignalCommand, self).__init__(delta)
        self.raw_data_vector = raw_data_vector
        self.samples = samples
        self.channels = channels
        self.timer = timer
        self.matrix = None
        self.sequence_trigger_vector = np.zeros((samples, 1))
        self.sequence_trigger_time_vector = np.zeros((samples, 1))
        self.cue_trigger_vector = np.zeros((samples, 1))
        self.cue_trigger_time_vector = np.zeros((samples, 1))        
        self.logger = logging.getLogger(__name__)
        
    def __reset_trigger_vectors__(self):
        self.sequence_trigger_vector[-1] = 0
        self.sequence_trigger_time_vector[-1] = 0        
        self.cue_trigger_vector[-1] = 0
        self.cue_trigger_time_vector[-1] = 0

    def is_valid(self):
        return self.raw_data_vector.size > 0
    
    def set_sequence_trigger(self, sequence_trigger_value):
        self.sequence_trigger_vector[-1] = sequence_trigger_value
        self.sequence_trigger_time_vector[-1] = self.timer.elapsedMicroSecs()
        
    def set_cue_trigger(self, cue_trigger_value):
        self.cue_trigger_vector[-1] = cue_trigger_value
        self.cue_trigger_time_vector[-1] = self.timer.elapsedMicroSecs()
    
    def set_decision(self, decision):
        self.decision = decision
        if self.decision:
            if self.matrix:
                if len(self.matrix.shape) > 1 and self.matrix.shape[1] > 0:
                    self.matrix[-1][-2] = -1
                    self.matrix[-1][-1] = self.decision

    def make_matrix(self):
        if self.raw_data_vector.shape != (self.samples, self.channels):
            #print("Raw vector = ", self.raw_data_vector, " shape = ", self.raw_data_vector.shape, " samples ", self.samples, " chaneels ", self.channels)
            self.data_matrix = self.raw_data_vector.reshape((self.samples, self.channels))
        else:
            self.data_matrix = self.raw_data_vector
            
        self.matrix = np.hstack((self.data_matrix, self.sequence_trigger_vector,
                                 self.sequence_trigger_time_vector, self.cue_trigger_vector,
                                 self.cue_trigger_time_vector))
        
        self.__reset_trigger_vectors__()
