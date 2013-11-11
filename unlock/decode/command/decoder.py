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

from unlock.decode.command.receiver import CommandReceiverFactory, CommandReceiver
from unlock.decode.classify import UnlockClassifier
from multiprocessing import Process, Queue
    
   
class InlineDecoder(object):
    def __init__(self, factory_method, signal, timer):
        super(InlineDecoder, self).__init__()
        self.factory_method = factory_method
        self.signal = signal
        self.timer = timer
        
    def shutdown(self):
        self.signal.stop()
        self.signal.close()
        
    def stop(self):
        raise Exception("Stop not supported")
        
    def create_receiver(self, args, classifier_type=None, chained_classifier=None):
        classifier_obj = UnlockClassifier.create(classifier_type, args)
        return CommandReceiverFactory.create(factory_method=self.factory_method, signal=self.signal,
                                             timer=self.timer, classifier=classifier_obj,
                                             chained_receiver=chained_classifier)
        
        
class MultiProcessDecoder(object):
    def __init__(self, args):
        super(MultiProcessDecoder, self).__init__()
        self.args = args
        self.mp_cmd_receiver = None
        
    def shutdown(self):
        if self.mp_cmd_receiver != None:
            self.mp_cmd_receiver.stop()
        
    def stop(self):
        pass    
        
    def create_receiver(self, args, classifier_type=None):
        self.mp_cmd_receiver = MultiProcessCommandReceiver(classifier_type, args, self.args)
        return self.mp_cmd_receiver
            
          