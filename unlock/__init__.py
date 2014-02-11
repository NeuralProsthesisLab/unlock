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

from unlock.util import *
from unlock.state import *
from unlock.view import *
from unlock.controller import *
from unlock.bci import *
from unlock import unlock_runtime

class UnlockFactory(object):
    def __init__(self, config):
        super(UnlockFactory, self).__init__()
        self.window = None
        self.bci_wrapper = None
        self.bci = None
        self.config = config
        self.receiver_factory = UnlockCommandReceiverFactory()
        self.decoder_factory = UnlockDecoderFactory()
        self.logger = logging.getLogger(__name__)

    def create_base(self):
        bci = self.inline()
        assert self.window
        canvas = UnlockControllerFactory.create_canvas(self.window.width, self.window.height)
        command_connected_fragment = self.create_command_connected_fragment(canvas, bci.receiver)
        return bci, canvas, command_connected_fragment

    def create_command_connected_fragment(self, canvas, stimuli, command_receiver):
        assert self.window
        return UnlockControllerFactory.create_command_connected_fragment(canvas, stimuli, command_receiver)

    def create_decoder(self, decoder):
        return self.decoder_factory.create_decoder(decoder['name'], **decoder['args'])

    def create_receiver(self, receiver_type, signal, timer, decoder):
        receiver = self.receiver_factory.create_receiver(receiver_type, signal=signal, timer=timer, decoder=decoder)
        return receiver

    def create_stimuli(self):
        assert self.context
        stimuli, views = getattr(self, self.config['bci']['stimuli'])
        return stimuli, views

    def create_quad_ssvep(self, canvas, color):
        stimuli, views = UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color)
        return stimuli, views

    def inline(self):
        # XXX - this is a hack because the context doesn't support keyword args.
        assert self.signal is not None and self.timer is not None
        decoder_args = self.config['bci']['decoder']
        decoder = self.create_decoder(decoder_args)

        receiver_type = self.config['bci']['receiver']
        receiver = self.create_receiver(receiver_type, self.signal, self.timer, decoder)
        bci = InlineBciWrapper(receiver, self.signal, self.timer)
        return bci

# XXX this is no longer used
    def multiprocess(self):
        bci_wrapper = MultiProcessBciWrapper(self.config)
        return bci_wrapper

    def nidaq(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_nidaq_signal(self.timer)
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

    def audio(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.AudioSignal()
        if not signal.start():
            raise RuntimeError('failed to start audio signal')

        return signal

    def enobio(self):
        assert 'mac_addr' in self.config['signal']
        mac_addr = [int(value,0) for value in [x.strip() for x in self.config['signal']['mac_addr'].split(',')]]

        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_enobio_signal(self.timer)
        if not signal.open(mac_addr):
            print('enobio did not open')
            raise RuntimeError('enobio did not open')
        if not signal.start():
            print('enobio device did not start streaming')
            raise RuntimeError('enobio device did not start streaming')
        return signal

    def mobilab(self):
        assert 'com_port' in self.config['bci']['signal']
        com_port = self.config['bci']['signal']['com_port']

        analog_channels_bitmask = 1+2+4+8+16+32+64+128
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_mobilab_signal(
            self.timer, analog_channels_bitmask, 0, com_port)

        if not signal.start():
            print('mobilab device did not start streaming')
            raise RuntimeError('mobilab device did not start streaming')
        return signal

    def file(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        raise Exception("FIX ME")
        signal = acquire.MemoryResidentFileSignal(self.config['bci']['signal']['file'],  #analysis/data/valid/emg_signal_1380649383_tongue_c.5_r.5_i1.txt',
            self.timer, channels=17)
        if not signal.start():
            print('file signal failed to start; filename = ', self.config['filename'])
            raise RuntimeError('file signal failed to start')
        return signal

    def random(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_random_signal(self.timer)
        signal.open([])
        signal.start()
        return signal

    def pyglet_window(self):
        assert 'fullscreen' in self.config['pyglet'] and 'fps' in self.config['pyglet'] and \
                'vsync' in self.config['pyglet']

        return PygletWindow(self.bci, self.config['pyglet']['fullscreen'], self.config['pyglet']['fps'],
            self.config['pyglet']['vsync'])

    def single_ssvep_diagnostic(self):
        print ("config = ", self.config['single_ssvep_diagnostic'], self.config['single_ssvep_diagnostic'])
        return UnlockControllerFactory.create_single_standalone_ssvep_diagnostic(self.window, self.bci.receiver,
            **self.config['single_ssvep_diagnostic'])

    def gridspeak(self):
        bci, canvas, command_connected_fragment = self.create_base()
        return UnlockControllerFactory.create_gridspeak(self.window, bci.receiver)

    def gridcursor(self):
        bci, canvas, command_connected_fragment = self.create_base()
        return UnlockControllerFactory.create_gridcursor(self.window, canvas, command_connected_fragment)

    def dashboard(self):
        import sys
        config = self.config['controllers']
        controllers = []

        for controller_attr in config:
            if controller_attr['name'] == 'dashboard':
                continue

            controller = getattr(self, controller_attr['name'])
            controllers.append(controller())

        bci, canvas, command_connected_fragment = self.create_base()
        return UnlockControllerFactory.create_dashboard(self.window, canvas, command_connected_fragment, controllers)

