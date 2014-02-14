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
from sqlalchemy import create_engine


class Stimulation(object):
    def __init__(self, stimuli, views):
        super(Stimulation, self).__init__()
        self.stimuli = stimuli
        self.views = views

class UnlockFactory(object):
    def __init__(self):
        super(UnlockFactory, self).__init__()
        self.receiver_factory = UnlockCommandFactory()
        self.decoder_factory = UnlockDecoderFactory()
        self.acquisition_factory = UnlockAcquisitionFactory()
        self.controller_factory = UnlockControllerFactory()
        self.state_factory = UnlockStateFactory()
        self.view_factory = UnlockViewFactory()

    def database(self, database=None, host=None, user=None, name=None, port=None, addr=None):
        assert database and host and user and name and port and addr
        engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (database, host, user, port, addr))
        return engine
        
    def logging(self, config):
        if config:
            logging.config.dictConfig(config['logging'])
        else:
            level = logging.DEBUG
            logging.basicConfig(level=level)
            
        return logging.getLogger(__name__)

    def nidaq(self):
        return self.acquisition_factory.create_nidaq()

    def audio(self):
        return self.acquisition_factory.create_audio_signal()

    def enobio(self, mac_addr_str='0x61,0x9c,0x58,0x80,0x07,0x00'):
        mac_addr = [int(value,0) for value in [x.strip() for x in mac_addr_str.split(',')]]
        return self.acquisition_factory.create_enobio_signal(mac_addr)

    def mobilab(self, com_port='COM7', channels_bitmask=0xff):
        return self.acquisition_factory.create_mobilab(com_port, channels_bitmask)

    def file(self, file=None, channels=17):
        assert file
        return self.acquisition_factory.create_file_signal(file, channels)

    def random(self):
        return self.acquisition_factory.create_random_signal()

    def pyglet(self, signal, **pyglet_args):
        assert 'fullscreen' in pyglet_args and 'fps' in pyglet_args and 'vsync' in pyglet_args
        return self.controller_factory.create_pyglet_window(signal, **pyglet_args)
            
    def quad_ssvep(self, canvas, stimulus='frame_count', color=[0,0,0], color1=[255,255,255], stimuli_duration=3.0,
            rest_duration=1.0, frequencies=[12.0,13.0,14.0,15.0], width=500, height=100, horizontal_blocks=5,
            vertical_blocks=1):

        stimuli = self.state_factory.create_stimuli(stimulus, frequencies, stimuli_duration, rest_duration)
        ssvep_views = self.view_factory.create_ssvep_views(stimuli, width, height, horizontal_blocks, vertical_blocks)
        return Stimulation(stimuli, ssvep_views)

    def harmonic_sum(self, buffering_decoder, threshold_decoder, fs=256, trial_length=3, n_electrodes=8,
                     targets=[12.0, 13.0, 14.0, 15.0], target_window=0.1, nfft=2048, n_harmonics=1):

        return self.create_decoder(buffering_decoder, threshold_decoder, **{'fs': fs, 'trial_length': trial_length,
            'n_electrodes': n_electrodes, 'targets': targets, 'target_window': target_window, 'nfft': nfft,
            'n_harmonics': n_harmonics})

    def gridspeak(self,stimulation=None, decoder=None):
        bci, canvas, command_connected_fragment = self.create_base()
        return self.controller_factory.create_gridspeak(self.window, bci.receiver)

    def gridcursor(self):
        bci, canvas, command_connected_fragment = self.create_base()
        return self.controller_factory.create_gridcursor(self.window, canvas, command_connected_fragment)



    def dashboard(self, stimulation=None, decoder=None, controllers=None):
        assert stimulation and decoder and controllers
        canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        receiver_args = {'signal': signal, 'timer': self.acquisition_factory.timer, 'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoded', **receiver_args)
        cc_frag = self.controller_factory.create_command_connected_fragment(canvas, stimulation.stimuli,
            stimulation.views, cmd_receiver)

        icons = []
        for c in controllers:
            icons.append((c.icon_path, c.name))

        state_chain, grid_state, state_chain = self.state_factory.create_dashboard_grid(controllers, icons)
        center_x, center_y = canvas.center()
        grid_view = self.view_factory.create_grid_view(grid_state, canvas, icons, center_x, center_y)

        return self.controller_factory.create_dashboard(self.window, canvas, cc_frag, controllers, grid_view, state_chain)

    def create_singleton(self, name, key, config):
        assert not hasattr(self, key)
        newobj = self.create(name, config)
        setattr(self, key, newobj)
        
    def create(self, name, config):
        objdesc = config[name]
        deps = None
        args = None
        
        if 'args' in objdesc:
            args = objdesc['args']
            
        if 'deps' in objdesc:
            for key, value in deps.items():
                if type(value) == list:
                    depobj = []
                    for element in value:
                        depobj.append(self.create(element, self.config[element]))
                else:             
                    depobj = self.create(value, self.config[value])
                    
                deps[key] = depobj
                
            if args and deps:
                args.update(deps)
                
        if args:    
            newobj = getattr(self, name)(**args)
        else:
            newobj = getattr(self, name)()

        if newobj is None:
            self.logger.error("UnlockFactory.create_"+str(name), "returned None; objdesc = ", objdesc)

        assert newobj        
        return newobj
