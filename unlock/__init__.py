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
    def __init__(self, canvas, stimuli, views):
        super(Stimulation, self).__init__()
        self.canvas = canvas
        self.stimuli = stimuli
        self.views = views

class UnlockFactory(AbstractFactory):
    def __init__(self):
        super(UnlockFactory, self).__init__()
        self.command_factory = UnlockCommandFactory()
        self.decoder_factory = UnlockDecoderFactory()
        self.acquisition_factory = UnlockAcquisitionFactory()
        self.controller_factory = UnlockControllerFactory()
        self.state_factory = UnlockStateFactory()
        self.view_factory = UnlockViewFactory()

    def database(self, host=None, user=None, name=None, port=None, addr=None):
        assert host and user and name and port and addr
        engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (name, host, user, port, addr))
        return engine
        
    def logging(self, **config):
        if config:
            logging.config.dictConfig(config)
        else:
            level = logging.DEBUG
            logging.basicConfig(level=level)
            
        return logging.getLogger(__name__)

    def nidaq(self):
        return self.acquisition_factory.create_nidaq_signal()

    def audio(self):
        return self.acquisition_factory.create_audio_signal()

    def enobio(self, mac_addr_str='0x61,0x9c,0x58,0x80,0x07,0x00'):
        mac_addr = [int(value,0) for value in [x.strip() for x in mac_addr_str.split(',')]]
        return self.acquisition_factory.create_enobio_signal(mac_addr)

    def mobilab(self, com_port='COM7', channels_bitmask=0xff):
        return self.acquisition_factory.create_mobilab_signal(com_port, channels_bitmask)

    def file(self, file=None, channels=17):
        assert file
        return self.acquisition_factory.create_file_signal(file, channels)

    def random(self):
        return self.acquisition_factory.create_random_signal()

    def pyglet(self, **pyglet_args):
        assert 'fullscreen' in pyglet_args and 'fps' in pyglet_args and 'vsync' in pyglet_args
        return self.controller_factory.create_pyglet_window(self.signal, **pyglet_args)
            
    def quad_ssvep(self, stimulus='frame_count', color=[0,0,0], color1=[255,255,255], stimuli_duration=3.0,
            rest_duration=1.0, frequencies=[12.0,13.0,14.0,15.0], width=500, height=100, horizontal_blocks=5,
            vertical_blocks=1):

        if stimulus == 'frame_count':
            stimulus = self.state_factory.create_frame_counted_timed_stimulus(frequencies[0])
            stimulus1 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[1])
            stimulus2 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[2])
            stimulus3 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[3])
        else:
            stimulus = self.state_factory.create_wall_clock_timed_stimulus(frequencies[0] * 2)
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[1] * 2)
            stimulus2 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[2] * 2)
            stimulus3 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[3] * 2)

        canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(stimuli_duration, rest_duration,  *[stimulus, stimulus1, stimulus2, stimulus3])
        ssvep_views = self.view_factory.create_quad_ssvep_views(stimuli, canvas, width, height, horizontal_blocks, vertical_blocks)
        #print("canvas, stimuli , ssvep_views ", canvas, stimuli, ssvep_views)
        return Stimulation(canvas, stimuli, ssvep_views)

    def single_ssvep(self, stimulus='frame_count', color=[0,0,0], color1=[255,255,255], stimuli_duration=3.0,
            rest_duration=1.0, frequency=15.0, width=300, height=300, horizontal_blocks=2,
            vertical_blocks=3, repeat_count=150):

        if stimulus == 'frame_count':
            stimulus = self.state_factory.create_frame_counted_timed_stimulus(frequency, repeat_count=repeat_count)
        else:
            stimulus = self.state_factory.create_wall_clock_timed_stimulus(frequency * 2)

        canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        #stimuli = self.state_factory.create_timed_stimuli(stimuli_duration, rest_duration,  *[stimulus])
        ssvep_views = self.view_factory.create_single_ssvep_view(stimulus, canvas, width, height, horizontal_blocks, vertical_blocks)
        return Stimulation(canvas, stimulus, ssvep_views)

    def single_msequence(self, stimulus='time', color=(0,0,0), color1=(255,255,255), stimulus_duration=3.0,
                         rest_duration=1.0, frequency=30.0, width=300, height=300, horizontal_blocks=2,
                         vertical_blocks=2, repeat_count=150):

        if stimulus == 'frame_count':
            stimulus = self.state_factory.create_frame_counted_timed_stimulus(frequency, repeat_count=repeat_count)
        else:
            stimulus = self.state_factory.create_wall_clock_timed_stimulus(frequency * 2)

        canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        msequence_views = self.view_factory.create_single_msequence_view(stimulus, canvas, width, height, horizontal_blocks, vertical_blocks)
        return Stimulation(canvas, stimulus, msequence_views)

    def harmonic_sum(self, buffering_decoder, threshold_decoder, fs=256, trial_length=3, n_electrodes=8,
                     targets=[12.0, 13.0, 14.0, 15.0], target_window=0.1, nfft=2048, n_harmonics=1):

        return self.decoder_factory.create_harmonic_sum_decision(buffering_decoder, threshold_decoder, **{'fs': fs, 'trial_length': trial_length,
            'n_electrodes': n_electrodes, 'targets': targets, 'target_window': target_window, 'nfft': nfft,
            'n_harmonics': n_harmonics})

    def fixed_time_buffering_decoder(self, window_length=768, electrodes=8):
        return self.decoder_factory.create_fixed_time_buffering(**{'window_length': window_length, 'electrodes': electrodes})

    def absolute_threshold_decoder(self, threshold, reduction_fn):
        return self.decoder_factory.create_absolute_threshold(**{'threshold': threshold, 'reduction_fn': reduction_fn})

    def no_stimulation(self):
        canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        return Stimulation(canvas, UnlockState(True), [])

    def gridspeak(self, stimulation=None, decoder=None, grid_radius=2, offline_data=False):
        assert stimulation and decoder
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer, 'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding', **receiver_args)

        grid_state = self.state_factory.create_grid_hierarchy(grid_radius)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('gridspeak')
            state_chain = self.state_factory.create_state_chain(grid_state, offline_data)
        else:
            state_chain = grid_state

        gridspeak_view = self.view_factory.create_gridspeak(grid_state, stimulation.canvas)

        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, state_chain,
            [gridspeak_view], name="Gridspeak", icon="gridspeak.png")

    def gridcursor(self, stimulation=None, decoder=None, grid_radius=2, offline_data=False):
        assert stimulation and decoder
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer, 'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding', **receiver_args)

        grid_state = self.state_factory.create_grid_hierarchy(grid_radius)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('gridspeak')
            state_chain = self.state_factory.create_state_chain(grid_state, offline_data)
        else:
            state_chain = grid_state

        gridspeak_view = self.view_factory.create_hierarchy_grid_view(grid_state, stimulation.canvas)

        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, state_chain,
            [gridspeak_view], name="Gridcursor", icon="gridcursor.png")

    def fastpad(self, stimulation=None, decoder=None, offline_data=False):
        assert stimulation and decoder
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer, 'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding', **receiver_args)

        fastpad_state = self.state_factory.create_fastpad()
        if offline_data:
            offline_data = self.state_factory.create_offline_data('fastpad')
            state_chain = self.state_factory.create_state_chain(fastpad_state, offline_data)
        else:
            state_chain = fastpad_state

        fastpad_view = self.view_factory.create_fastpad_view(fastpad_state, stimulation.canvas)
        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, state_chain,
            [fastpad_view], name="Fastpad", icon="fastpad.png")

    def time_scope(self, stimulation=None, channels=1, fs=256, duration=2, offline_data=False):
        assert stimulation
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer}
        cmd_receiver = self.command_factory.create_receiver('raw', **receiver_args)

        scope_model = TimeScopeState(channels, fs, duration)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('time_scope')
            state_chain = self.state_factory.create_state_chain(scope_model, offline_data)
        else:
            state_chain = scope_model

        time_scope_view = TimeScopeView(scope_model, stimulation.canvas)
        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, state_chain,
            [time_scope_view], name='TimeScope', icon='time-128x128.jpg')

    def frequency_scope(self, stimulation=None, channels=1, fs=256, duration=2, offline_data=False):
        assert stimulation
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer}
        cmd_receiver = self.command_factory.create_receiver('raw', **receiver_args)

        scope_model = FrequencyScopeState(channels, fs, duration)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('time_scope')
            state_chain = self.state_factory.create_state_chain(scope_model, offline_data)
        else:
            state_chain = scope_model

        frequency_scope_view = FrequencyScopeView(scope_model, stimulation.canvas, labels=scope_model.labels)
        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, state_chain,
            [frequency_scope_view], name='FrequencyScope', icon='frequency2-128x128.png')

    def dashboard(self, stimulation=None, decoder=None, controllers=None, offline_data=False):
        assert stimulation and decoder
        if not controllers:
            controllers = []
        #canvas = self.controller_factory.create_canvas(self.window.width, self.window.height)
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer, 'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding', **receiver_args)
        cc_frag = self.controller_factory.create_command_connected_fragment(stimulation.canvas, stimulation.stimuli,
            stimulation.views, cmd_receiver)

        icons = []
        for c in controllers:
            icons.append((c.icon_path, c.name))

        grid_state = self.state_factory.create_grid_state(controllers, icons)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('dashboard')
            state_chain = self.state_factory.create_state_chain(grid_state, offline_data)
        else:
            state_chain = grid_state

        grid_view = self.view_factory.create_grid_view(grid_state, stimulation.canvas, icons)
        return self.controller_factory.create_dashboard(self.window, stimulation.canvas, controllers, cc_frag,
            [grid_view], state_chain)

    def ssvep_diagnostic(self, stimulation=None, decoder=None, output_file='ssvep-diagnostic', duration=10, standalone=True):
        receiver_args = {'signal': self.signal, 'timer': self.acquisition_factory.timer}
        if decoder:
            receiver_args['decoder'] = decoder
            cmd_receiver = self.command_factory.create_receiver('decoding', **receiver_args)
        else:
            cmd_receiver = self.command_factory.create_receiver('raw', **receiver_args)

        cc_frag = self.controller_factory.create_command_connected_fragment(stimulation.canvas, stimulation.stimuli,
            stimulation.views, cmd_receiver)

        offline_data = self.state_factory.create_offline_data(output_file)
        return self.controller_factory.create_controller_chain(self.window, stimulation, cmd_receiver, offline_data, [],
            standalone=standalone)
