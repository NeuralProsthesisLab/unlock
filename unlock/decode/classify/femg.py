# Copyright (c) Byron Galbraith, James Percent, and Unlock contributors.
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

from unlock.decode.classify.classify import UnlockClassifier
#from classify import UnlockClassifier
import numpy as np


class FacialEMGDetector(UnlockClassifier):
    """
    Classifies facial EMG activity from bipolar electrodes placed to the
    left, right, and below the mouth. The signals are decoded to infer one of
    four movements:

    Left - only left channel active
    Right - only right channel active
    Down - left and right channel active
    Up - all channels active

    The decision to analyze the signal for activity is triggered by an eye
    blink event. Channel activation is determined by checking if the maximum
    RMS value computed over the window of interest is greater than a
    user-supplied threshold value.
    """
    Left = 0
    Bottom = 1
    Right = 2
    Select = 3
    
    def __init__(self, rms_thresholds, channels=4, window_size=22050):
        super(FacialEMGDetector, self).__init__()
        self.thresholds = rms_thresholds
        self.channels = channels
        self.window_size = window_size
        self.window = np.zeros((window_size, channels))

        # The state of whether the maximum rms value of a channel
        # (Left, Right, Bottom) is above threshold. Ordered to coincide with
        # the control scheme of Up,Down,Left,Right
        self.decision_patterns = np.array([
            [True, True, True],  # Up/Forward
            [True, True, False],  # Down/Backward
            [True, False, False],  # Left
            [False, True, False]  # Right
        ])

    def classify(self, command):
        """
        1. Compute RMS of incoming samples
        2. Place RMS values in a buffer
        2. Determine if an eye blink has occurred
        3. If eye blink, evaluate buffer for emg activity
        """
        if not command.is_valid():
            return command
            
        samples = command.data_matrix[0:self.channels]
        rms = np.sqrt(np.mean(samples**2, axis=0))
        
        self.window = np.roll(self.window, -1, axis=0)
        self.window[-1] = rms
        
        activations = np.max(self.window, axis=0) > self.thresholds
        if activations[FacialEMGDetector.Select]:
            decision = None
            for i, pattern in enumerate(self.decision_patterns):
                if np.array_equal(activations[0:3], pattern):
                    decision = i + 1
            if decision is not None:
                command.decision = decision
                self.window = np.zeros((self.window_size, self.channels))
                
        return command
    

def test_facial_emg_detector():
    class Command(object):
        def __init__(self):
            self.validity = True
            self.data_matrix = None
            
        def is_valid(self, ):
            return self.validity
        
        
    
    f = FacialEMGDetector(None)
    assert f is not None
    


if __name__ == '__main__':
    test_facial_emg_detector()