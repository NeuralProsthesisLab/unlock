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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.import socket
  
import numpy as np
import random

class RMSSignalGenerator(object):
    '''
        Generates simulated device samples.  Each invocation of the
        generate method returns a table of samples.  The generate method determines sample values
        by consulting an unlock.util.SequenceState.  The state returns a tuple of True/False values,
        one foreach channel.  A state channel value that is True results in sample value, for the
        corresponding channel, that is above the threshold; a False value results in value above
        the min, but below the threshold.
                
        channels:   number of channels
        minmax:     list of tuples denoting the min and max values of a channel
        thresholds: list of channel thresholds
        state:      an unlock.util.SequenceState.  provides a means to dynamically configure
                    which channels of a given set of samples are above/below threshold values
        samples:    default number of samples per request
    '''            
    def __init__(self, channels, minmax, thresholds, state, samples, seed=31337):
        assert channels == len(thresholds) and channels == len(minmax)
        self.channels = channels
        self.min = 0
        self.max = 1
        self.minmax = minmax
        self.thresholds = thresholds
        self.samples = samples
        self.state = state
        self.state.start()
        self.generate_sample = self.simple_sample_gen
        self.random = random.Random()
        self.random.seed(seed)
        
    def generate_samples(self, samples=None):
        if samples == None:
            samples = self.samples
            
        ret = np.zeros((samples, self.channels))
        for sample in range(samples):
            ret[sample] = self.generate_sample(self.state.state())
        self.state.step()
        return ret
    
    def simple_sample_gen(self, state_value):
        assert self.channels == len(state_value)
        sample = np.zeros(self.channels)
        for i in range(self.channels):
            if state_value[i] == True:
                sample[i] =  self.random.randint(self.thresholds[i], self.minmax[i][self.max])
            elif state_value[i] == False:
                sample[i] = self.random.randint(self.minmax[i][self.min], self.thresholds[i]-1)
            else:
                raise Exception('invalid state')
        return sample
            
if __name__ == '__main__':
    # example 
    from unlock.util.state import SequenceState
    channels = 4
    minmax = [(0,10), (-10, 10), (9,100), (0,7)]
    thresholds = [ 8, 5, 80, 5]
    samples = 12
    seq = [(False, False, False, False), (True, False, False, False), (True, True, False, False),
        (False, False, False, True), (False, True, False, False), (True, False, True, False),
        (False, False, True, False), (False, False, False, True),
        (True, False, False, True), (False, True, False, True), (True, True, True, False),
        (True, True, True, True)]
    state = SequenceState(seq)
    print(state.sequence)
    gen = RMSSignalGenerator(channels, minmax, thresholds, state, samples)
    sample_values = gen.generate_samples()
    for i in range(len(seq)):
        print ("Sequence value   = ", seq[i])
        print("Normalized Sample = ", sample_values[i] - np.array(thresholds))
        print('-'*80)
    