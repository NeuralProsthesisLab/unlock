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

from unlock.decode.classify import FacialEMGDetector
from unlock.state import SequenceState
from unlock.decode import acquire
from unlock.decode import GeneratedSignalReceiver, ClassifiedCommandReceiver
from unlock.util import RMSSignalGenerator
import time
import unittest
import pyglet


class FacialEMGDectectorTests(unittest.TestCase):       
    def testClassify(self):
       # print ("opbject sin classif y = ", dir(unlock.decode.classify))

        channels = 4
        minmax = [(0,10), (-4, 10), (9,100), (0,7)]
        thresholds = [ 8, 5, 80, 5]
        samples = 12
        seq = [
            (False, False, False, False), (False, False, False, True),
            (True, False, False, False), (False, False, False, True),
            (False, False, True, False), (False, False, False, True),
            (True, False, True, False), (False, False, False, True),
            (True, True, True, False), (False, False, False, True)]
        state = SequenceState(seq)
        
        emg = FacialEMGDetector(thresholds, channels=4, window_size=10)
        timer = acquire.create_timer()
        signal = RMSSignalGenerator(channels, minmax, thresholds, state, samples)
        
        command_receiver = GeneratedSignalReceiver(signal, timer)
        classified_command_receiver = ClassifiedCommandReceiver(command_receiver, emg)
        #print ("Thresholds = ", thresholds)
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None

        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision == FacialEMGDetector.LeftDecision
        
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision == FacialEMGDetector.RightDecision        
        
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)        
        assert command.decision == FacialEMGDetector.DownDecision
        
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision is None
        command = classified_command_receiver.next_command(time.time())
        #print("decision = ", command.decision)
        assert command.decision == FacialEMGDetector.UpDecision
        
        
def getSuite():
    return unittest.makeSuite(FacialEMGDetectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    
