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

import unlock.bci


class UnlockDecoder(object):
    HarmonicSumDecision = 0
    EyeBlinkDetector = 1
    FacialEMGDetector = 2
    UnknownDecoder = 3

    def __init__(self, task_state=None):
        super(UnlockDecoder, self).__init__()
        self.task_state = task_state
        
    def classify(self, command):
        return command
        
    def reset(self):
        pass
    
    @staticmethod
    def create(decoder, kwargs):
        if decoder == UnlockDecoder.HarmonicSumDecision or decoder is None:
            return unlock.bci.hsd.new_fixed_time_threshold_hsd(**kwargs)
        elif decoder == UnlockDecoder.EyeBlinkDetector:
            return unlock.bci.EyeBlinkDetector(**kwargs)
        elif decoder == UnlockDecoder.FacialEMGDetector:
            return unlock.bci.FacialEMGDetector(**kwargs)
        elif decoder == UnlockDecoder.UnknownDecoder:
            return unlock.bci.UnlockDecoder(**kwargs)
        else:
            raise Exception("Undefined Decoder: ", decoder, " kwargs = ", kwargs)
            
            