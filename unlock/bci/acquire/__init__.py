# Copyright (c) James Percent and Unlock contributors.
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

import sys
import time

imported_neural_signal = False

try:
    from unlock.bci.acquire.neuralsignal import create_timer, create_nonblocking_mobilab_signal, create_nonblocking_enobio_signal, create_random_signal, create_nidaq_signal
    imported_neural_signal = True
except:
    assert sys.platform == 'darwin'

from unlock.bci.acquire.audio_signal import *
from unlock.bci.acquire.file_signal import *


class BasicTimer(object):
    def __init__(self):
        self.start = time.time()

    def elapsedMicroSecs(self):
        return time.time() - self.start


class UnlockAcquisitionFactory:
    def __init__(self):
        if imported_neural_signal:
            self.timer = create_timer()
        else:
            self.timer = BasicTimer

    def create_nidaq_signal(self):
        signal = create_nidaq_signal()
        if not signal.start():
            raise RuntimeError('Failed to start National Instruments DAQ')
        return signal
        #for j in range(50):
        #	ret = daq.acquire()
        #	ret = daq.getdata(ret)
        #	f = open('test.data', 'wb')
        #	import numpy as np
        #	a = np.array(ret, dtype='float64')
        #	a = a.reshape((500, 4))
        #	#np.savetxt(f, a, fmt='%d', delimiter='\t')
        #	for i in range(20):
        #		print(a[i])
        #

    def create_audio_signal(self):
        signal = AudioSignal()
        if not signal.start():
            raise RuntimeError('failed to start audio signal')
        return signal

    def create_enobio_signal(self, mac_addr):
        assert 'mac_addr' in self.config['signal']
        mac_addr = [int(value,0) for value in [x.strip() for x in self.config['signal']['mac_addr'].split(',')]]
        signal = create_nonblocking_enobio_signal(self.timer)
        if not signal.open(mac_addr):
            print('enobio did not open')
            raise RuntimeError('enobio did not open')
        if not signal.start():
            print('enobio device did not start streaming')
            raise RuntimeError('enobio device did not start streaming')
        return signal

    def create_mobilab_signal(self, com_port, analog_channels_bitmask):
        #assert 'com_port' in self.config['bci']['signal']
        #com_port = self.config['bci']['signal']['com_port']

        #analog_channels_bitmask = 1+2+4+8+16+32+64+128
        from unlock.bci import acquire
        #timer = acquire.create_timer()
        signal = create_nonblocking_mobilab_signal(
            self.timer, analog_channels_bitmask, 0, com_port)

        if not signal.start():
            print('mobilab device did not start streaming')
            raise RuntimeError('mobilab device did not start streaming')
        return signal

    def create_file_signal(self, timer):
        from unlock.bci import acquire
        timer = acquire.create_timer()
        raise Exception("FIX ME")
        signal = acquire.MemoryResidentFileSignal(self.config['bci']['signal']['file'], timer, channels=17)  #analysis/data/valid/emg_signal_1380649383_tongue_c.5_r.5_i1.txt',

        if not signal.start():
            print('file signal failed to start; filename = ', self.config['filename'])
            raise RuntimeError('file signal failed to start')
        return signal

    def create_random_signal(self):
        from unlock.bci import acquire
        signal = create_random_signal(self.timer)
        signal.open([])
        signal.start()
        return signal


#try:
#    from .nidaq import *
#except:
#    print ("unlock.acquire NOTICE: NI DAQ software not installed.. ")
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
