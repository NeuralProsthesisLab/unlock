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

from unlock.bci.command.receiver import *
from unlock.bci.command.command import *
from unlock.bci.acquire import MemoryResidentFileSignal
    
class UnlockCommandFactory(object):
    def __init__(self):
        super(UnlockCommandFactory, self).__init__()
        
    def create_receiver(self, receiver_type='inline', **kwargs):
        receiver_factory_method = {
            'delta': self.create_delta_receiver,
            'raw': self.create_raw_receiver,
            'decoding': self.create_decoding_receiver,
            'datagram': self.create_datagram_receiver,
            'inline': self.create_inline_receiver
        }.get(receiver_type, self.unknown)
            
        if receiver_factory_method is None:
            raise LookupError('CommandReceiver does not support the factory method identified by '+str(receiver_factory_method))
                
        return receiver_factory_method(**kwargs)
            
    def create_delta_receiver(self):
        return DeltaCommandReceiver()
        
    def create_raw_receiver(self, signal=None, timer=None):
        if type(signal) == MemoryResidentFileSignal:
            print("creating memory resident file signal")
            receiver = FileSignalReceiver(signal, timer)
        else:
            receiver = RawInlineSignalReceiver(signal, timer)
            
        return receiver
        
    def create_datagram_receiver(self, source=None):
        return DatagramCommandReceiver(source) 
        
    def create_decoding_receiver(self, signal=None, timer=None, decoder=None):
        receiver = self.create_raw_receiver(signal, timer)
        return DecodingCommandReceiver(receiver, decoder)       
        
    def create_inline_receiver(self):
        return InlineCommandReceiver()

    def unknown(self, **kwargs):
        raise("Unsupported")