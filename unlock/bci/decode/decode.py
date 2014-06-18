# Copyright (c) James Percent, Byron Galibrith and Unlock contributors.
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

import unlock.bci
import numpy as np
from unlock.state import TrialState
from sklearn import lda


class UnlockDecoder(object):
    def __init__(self, task_state=None):
        super(UnlockDecoder, self).__init__()
        self.task_state = task_state
        self.started = False
        
    def decode(self, command):
        ''' You do your business here '''
        return command
        
    def update(self, command):
        ''' And you do more business here '''
        return command
        
    def start(self):
        self.started = True
        
    def stop(self):
        self.started = False
        
    def reset(self):
        pass
        
        
class UnlockDecoderChain(UnlockDecoder):
    def __init__(self):
        self.decoders = []
        
    def add(self, decoder):
        self.decoders.append(decoder)
        
    def decode(self, command):
        for decoder in self.decoders:
            command = decoder.decode(command)
            if not command.is_ready():
                return command
                
        for decoder in self.decoders:
            command = decoder.update(command)
        return command
            
    def start(self):
        for decoder in self.decoders:
            decoder.start()
            
    def stop(self):
        for decoder in self.decoders:
            decoder.stop()
            
    def reset(self):
        for decoder in self.decoders:
            self.decoder.reset()
            
            
class TrialStateControlledDecoder(UnlockDecoder):
    def __init__(self, task_state):
        self.task_state = task_state
        
    def decode(self, command):
        """
        Check if the task state has entered or left a rest state and handles
        accordingly.
        """
        if self.task_state is not None:
            state_change = self.task_state.get_state()
            if state_change == TrialState.RestExpiry:
                self.start()
            elif state_change == TrialState.TrialExpiry:
                self.stop()
        return command
        
        
class BufferedDecoder(UnlockDecoder):
    def __init__(self, buffer_shape, electrodes):
        super(BufferedDecoder, self).__init__()
        self.buffer = np.zeros(buffer_shape)
        self.electrodes = electrodes
        self.cursor = 0
        
    def decode(self, command):
        """
        Determines how to buffer incoming data samples. By default, samples
        are added from the beginning of the buffer until it is full, then
        further samples cause the early samples to be discarded.
        data is assumed to have a shape of (n_samples, n_channels)
        """
        if not command.is_valid() or not self.started:
            return command
        
        data = command.matrix[:, 0:self.electrodes]
            
        n_samples = data.shape[0]
        if self.cursor + n_samples >= self.buffer.shape[0]:
            shift = self.cursor + n_samples - self.buffer.shape[0]
            self.buffer = np.roll(self.buffer, -shift, axis=0)
            self.buffer[-n_samples:] = data
            self.cursor = self.buffer.shape[0]
        else:
            self.buffer[self.cursor:self.cursor+n_samples] = data
            self.cursor += n_samples

        if self.is_ready():
            command.buffered_data = self.get_data()
            command.set_ready_value(True)
        else:
            command.set_ready_value(False)
        return command
            
    def get_data(self):
        """
        Returns the buffered data according to the cursor position.
        """
        return self.buffer[0:self.cursor]
        
    def is_ready(self):
        pass
        
    def handle_result(self, result):
        pass
        
        
class FixedTimeBufferingDecoder(BufferedDecoder):
    def __init__(self, electrodes, window_length):
        buffer_shape = (window_length, electrodes)
        super(FixedTimeBufferingDecoder, self).__init__(buffer_shape, electrodes)
        self.window_length = window_length
        self.decode_now = False
        
    def decode(self, command):
        command = super(FixedTimeBufferingDecoder, self).decode(command)
        return command
        
    def stop(self):
        self.started = False
        if self.cursor >= 0.9*self.window_length:
            self.decode_now = True
            
    def is_ready(self):
        return self.cursor >= self.window_length or self.decode_now
        
    def update(self, command):
        self.decode_now = False
        self.cursor = 0
        return command
        
        
class SlidingWindowDecoder(BufferedDecoder):
    def __init__(self, step_size=32, trial_limit=768, electrodes=8):
        buffer_shape = (trial_limit, electrodes)
        super(SlidingWindowDecoder, self).__init__(buffer_shape, electrodes)
        self.step_size = step_size
        self.trial_limit = trial_limit
        self.last_mark = 0
        
    def is_ready(self):
        return self.cursor >= self.last_mark + self.step_size
        
    def update(self, command):
        if command.result or self.cursor >= self.trial_limit:
            self.last_mark = 0
            self.cursor = 0
        else:
            self.last_mark = self.cursor + self.step_size
        return command
        
        
class NoThresholdDecoder(UnlockDecoder):
    """Accepts everything"""
    def decode(self, command):
        assert hasattr(command, 'features')
        command.confidence = 1.0
        command.accept = True
        return command
        
        
class AbsoluteThresholdDecoder(UnlockDecoder):
    """Accepts everything greater than or equal to a set value."""
    def __init__(self, threshold=0, reduction_fn='np.mean'):
        self.threshold = threshold
        self.reduction_fn = eval(reduction_fn)
        
    def decode(self, command):
        assert hasattr(command, 'features')
        command.confidence = 1.0
        command.accept = self.reduction_fn(command.features) >= self.threshold
        return command
        
        
class LdaThresholdDecoder(UnlockDecoder):
    """
    Uses an LDA decoder to determine the threshold boundary. LDA predictions
    above a provided confidence level are accepted. Training data must be
    supplied to the decoder.
    """
    def __init__(self, x=(0, 1), y=(0, 1), min_confidence=0.5,
                 reduction_fn='np.mean'):
        self.min_confidence = min_confidence
        self.clf = lda.LDA()
        self.clf.fit(x, y)
        self.reduction_fn = eval(reduction_fn)
        
    def decode(self, command):
        assert hasattr(command, 'features')
        command.confidence = self.clf.predict_proba(
            self.reduction_fn(command.features))[0, 1]
        command.accept = command.confidence >= self.min_confidence
        return command

