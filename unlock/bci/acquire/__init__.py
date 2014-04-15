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
no_bci = False

try:
    #from unlock.bci.acquire.neuralsignal import create_timer
    from unlock.bci.acquire.random_signal import create_timer, create_random_signal
    imported_neural_signal = True
except:
    assert sys.platform == 'darwin' or sys.platform == 'linux'
    no_bci = True

try:
    from unlock.bci.acquire.mobilab_signal import create_nonblocking_mobilab_signal
except Exception as e:
    print("unlock/acquire.__init__.py: mobilab not present", e)

try:
    from unlock.bci.acquire.enobio_signal import create_nonblocking_enobio_signal
except:
    print("unlock/acquire.__init__.py: enobio not present")

try:
    from unlock.bci.acquire.nidaq_signal import create_nidaq_signal
except:
    print("unlock/acquire.__init__.py: nidaq not present")

from unlock.bci.acquire.audio_signal import *
from unlock.bci.acquire.file_signal import *

class NoBciRandomSignal(object):
    def __init__(self,channels=8, seed=42, lower_bound=1, upper_bound=65536):
        super(NoBciRandomSignal, self).__init__()
        import random
        self.chans = channels
        self.rand = random.Random()
        self.rand.seed(seed)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
    
    def open(self, macaddr):
        self.mac = macaddr
        return True
            
    def init(self, channels):
        self.chans = channels
        return True
        
    def channels(self):
            return self.chans
            
    def start(self):
            return True
            
    def acquire(self):
            return 1 * self.chans
            
    def getdata(self, samples):
        import numpy as np
        ret = np.array([float(self.rand.randint(self.lower_bound, self.upper_bound)) for i in range(0, samples)])
        ret[-1] = 0
        return ret
    
    def getEaplsedMicros(self):
            pass
            
    def timestamp(self):
            pass
            
    def stop(self):
            pass
            
    def close(self):        
        pass

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
            self.timer = BasicTimer()

    def create_nidaq_signal(self, channel, channel_count):
        signal = create_nidaq_signal(self.timer, channel, channel_count)
        if not signal.start():
            raise RuntimeError('Failed to start National Instruments DAQ')
        return signal
        #for j in range(50):
        #       ret = daq.acquire()
        #       ret = daq.getdata(ret)
        #       f = open('test.data', 'wb')
        #       import numpy as np
        #       a = np.array(ret, dtype='float64')
        #       a = a.reshape((500, 4))
        #       #np.savetxt(f, a, fmt='%d', delimiter='\t')
        #       for i in range(20):
        #               print(a[i])
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
        from unlock.bci import acquire
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
        if no_bci:
            signal = NoBciRandomSignal()
        else:
            from unlock.bci import acquire
            signal = create_random_signal(self.timer)
        signal.open([])
        signal.start()
        return signal

