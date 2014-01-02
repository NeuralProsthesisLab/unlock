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

#import os
#import sys
#import platform
#import shutil
#import inspect

from unlock.bci.acquire import *
from unlock.bci.decode import *
from unlock.bci.command import *


from unlock.bci.command.receiver import CommandReceiverFactory, CommandReceiver
#from unlock.bci.decode import UnlockDecoder
from multiprocessing import Process, Queue
    
# XXX - this is awful

class InlineBciWrapper(object):
    def __init__(self, factory_method, signal, timer):
        super(InlineBciWrapper, self).__init__()
        self.factory_method = factory_method
        self.signal = signal
        self.timer = timer
        
    def shutdown(self):
        self.signal.stop()
        self.signal.close()
        
    def stop(self):
        raise Exception("Stop not supported")
        
    def create_receiver(self, args, decoder_type=None, chained_decoder=None):
        decoder_obj = UnlockDecoder.create(decoder_type, args)
        return CommandReceiverFactory.create(factory_method=self.factory_method, signal=self.signal,
                                             timer=self.timer, decoder=decoder_obj,
                                             chained_receiver=chained_decoder)
        
        
class MultiProcessBciWrapper(object):
    def __init__(self, args):
        super(MultiProcessBciWrapper, self).__init__()
        self.args = args
        self.mp_cmd_receiver = None
        
    def shutdown(self):
        if self.mp_cmd_receiver != None:
            self.mp_cmd_receiver.stop()
            
    def stop(self):
        pass    
        
    def create_receiver(self, args, decoder_type=None):
        self.mp_cmd_receiver = MultiProcessCommandReceiver(decoder_type, args, self.args)
        return self.mp_cmd_receiver
            
            
#
#def machine():
#    """Return type of machine."""
#    if os.name == 'nt' and sys.version_info[:2] < (2,7):
#        return os.environ.get("PROCESSOR_ARCHITEW6432", 
#               os.environ.get('PROCESSOR_ARCHITECTURE', ''))
#    else:
#        return platform.machine()
#
#def arch(machine=machine()):
#    """Return bitness of operating system, or None if unknown."""
#    machine2bits = {'AMD64': 64, 'x86_64': 64, 'i386': 32, 'x86': 32}
#    return machine2bits.get(machine, None)
#
#print (os_bits())
#
#from fakebci import *
#
#def create_so():
#    base_dir = os.path.dirname(inspect.getabsfile(FakeBCI))
#
#    if sys.platform == 'darwin':
#        boosted_bci = os.path.join(base_dir, 'boosted_bci.so')
#        if not os.path.exists(boosted_bci):
#            if platform.architecture()[0] == '64bit':
#                shutil.copyfile(os.path.join(base_dir, 'libboosted_bci_darwin_x86_64.so'), boosted_bci)
#            else:
#                raise NotImplementedError("32 bit OS X is currently untested")
#            
#    if sys.platform == 'win32':
#        boosted_bci = os.path.join(base_dir, 'boosted_bci.pyd')
#        if not os.path.exists(boosted_bci):
#            shutil.copyfile(os.path.join(base_dir, 'boosted_bci_win_x86.dll'), boosted_bci)            
#        os.environ['PATH']=os.environ['PATH']+';'+base_dir+'\\boost\\win-x86\\lib'
#            
#try:
#    import boosted_bci
#except:
#    print "Platform specific bci files have not been created"
