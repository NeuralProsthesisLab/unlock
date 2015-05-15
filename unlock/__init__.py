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

    ###########################################################################
    ## Logging
    ###########################################################################
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

    ###########################################################################
    ## Data Acquisition
    ###########################################################################
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

    def lsl(self, stream_name, stream_type):
        return self.acquisition_factory.create_lsl_signal(stream_name,
                                                          stream_type)

    ###########################################################################
    ## Display
    ###########################################################################
    def pyglet(self, **pyglet_args):
        assert 'fullscreen' in pyglet_args and 'fps' in pyglet_args and 'vsync' in pyglet_args
        return self.controller_factory.create_pyglet_window(self.signal, **pyglet_args)

    ###########################################################################
    ## Stimuli
    ###########################################################################
    def quad_ssvep(self, cb_properties=None, stimulus='time',
                   frequencies=(12.0, 13.0, 14.0, 15.0), stimuli_duration=3.0,
                   rest_duration=1.0):
        assert cb_properties

        if stimulus == 'frame_count':
            stim1 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[0])
            stim2 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[1])
            stim3 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[2])
            stim4 = self.state_factory.create_frame_counted_timed_stimulus(frequencies[3])
        else:
            stim1 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[0] * 2)
            stim2 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[1] * 2)
            stim3 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[2] * 2)
            stim4 = self.state_factory.create_wall_clock_timed_stimulus(frequencies[3] * 2)

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            stimuli_duration, rest_duration, *[stim1, stim2, stim3, stim4])
        ssvep_views = self.view_factory.create_quad_ssvep_views(
            stimuli, canvas, cb_properties)

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

    def single_dynamic_ssvep(self, cb_properties=None, stimulus='time',
                             frequency=10.0, trial_duration=3.0,
                             rest_duration=1.0):
        assert cb_properties
        if stimulus == 'frame_count':
            raise NotImplementedError('frame count not supported')
        else:
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency)

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            trial_duration, rest_duration, stimulus1)
        msequence_views = self.view_factory.create_single_ssvep_view(
            stimulus1, canvas, cb_properties)
        return Stimulation(canvas, stimuli, msequence_views)

    def single_msequence(self, cb_properties=None, stimulus='time',
                         frequency=30.0, repeat_count=150, sequence=(0,1)):
        assert cb_properties
        if stimulus == 'frame_count':
            stimulus = self.state_factory.create_frame_counted_timed_stimulus(
                frequency, repeat_count=repeat_count, sequence=sequence)
        else:
            stimulus = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequence)

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        msequence_views = self.view_factory.create_single_msequence_view(
            stimulus, canvas, cb_properties)
        return Stimulation(canvas, stimulus, msequence_views)

    def single_dynamic_msequence(self, cb_properties=None, stimulus='time',
                                 frequency=30.0, trial_duration=12.0,
                                 rest_duration=1.0):
        assert cb_properties
        if stimulus == 'frame_count':
            raise NotImplementedError('frame count not supported')
        else:
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency)

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            trial_duration, rest_duration, stimulus1)
        msequence_views = self.view_factory.create_single_msequence_view(
            stimulus1, canvas, cb_properties)
        return Stimulation(canvas, stimuli, msequence_views)

    def quad_msequence(self, cb_properties=None, stimulus='time',
                       frequency=30.0, trial_duration=12.0, rest_duration=1.0,
                       sequences=None):
        assert cb_properties and sequences
        if stimulus == 'frame_count':
            raise NotImplementedError('frame count not supported')
        else:
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[0])
            stimulus2 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[1])
            stimulus3 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[2])
            stimulus4 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[3])

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            trial_duration, rest_duration, stimulus1, stimulus2, stimulus3,
            stimulus4)
        #stimuli.stimuli[0].seq_state.outlet = self.signal.outlet
        msequence_views = self.view_factory.create_quad_msequence_view(
            [stimulus1, stimulus2, stimulus3, stimulus4], canvas,
            cb_properties)
        return Stimulation(canvas, stimuli, msequence_views)

    def dual_image_cvep(self, filenames, stimulus='time',
                       frequency=30.0, trial_duration=12.0, rest_duration=1.0,
                       sequences=None):
        if stimulus == 'frame_count':
            raise NotImplementedError('frame count not supported')
        else:
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[0])
            stimulus2 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[1])

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            trial_duration, rest_duration, stimulus1, stimulus2)
        msequence_views = self.view_factory.create_dual_image_cvep_view(
            [stimulus1, stimulus2], canvas, filenames)
        return Stimulation(canvas, stimuli, msequence_views)

    def dual_overlapping_cvep(self, cb_properties=None, stimulus='time',
                       frequency=30.0, trial_duration=12.0, rest_duration=1.0,
                       sequences=None):
        assert cb_properties and sequences
        if stimulus == 'frame_count':
            raise NotImplementedError('frame count not supported')
        else:
            stimulus1 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[0])
            stimulus2 = self.state_factory.create_wall_clock_timed_stimulus(
                frequency, sequence=sequences[1])

        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        stimuli = self.state_factory.create_timed_stimuli(
            trial_duration, rest_duration, stimulus1, stimulus2)
        msequence_views = self.view_factory.create_dual_overlapping_cvep_view(
            [stimulus1, stimulus2], canvas, cb_properties)
        return Stimulation(canvas, stimuli, msequence_views)


    def checkerboard_properties(self, width=300, height=300, x_tiles=4,
                                y_tiles=4, x_ratio=1, y_ratio=1,
                                color1=(0, 0, 0), color2=(255, 255, 255)):
        return CheckerboardProperties(width, height, x_tiles, y_tiles, x_ratio,
                                      y_ratio, color1, color2)

    def checkerboard_properties_list(self, width=(300,), height=(300,),
                                     x_tiles=(4,), y_tiles=(4,), x_ratio=(1,),
                                     y_ratio=(1,), color1=((0, 0, 0),),
                                     color2=((255, 255, 255),)):
        properties = list()
        for i in range(len(width)):
            properties.append(CheckerboardProperties(width[i], height[i],
                                                     x_tiles[i], y_tiles[i],
                                                     x_ratio[i], y_ratio[i],
                                                     color1[i], color2[i]))
        return properties

    ###########################################################################
    ## Decoders
    ###########################################################################
    def harmonic_sum(self, buffering_decoder, threshold_decoder, selector=None,
                     fs=256, n_electrodes=8, target_window=0.1, nfft=2048,
                     n_harmonics=1, targets=(12.0,13.0,14.0,15.0),
                     selected_channels=None):
        return self.decoder_factory.create_harmonic_sum_decision(
            buffering_decoder, threshold_decoder, selector=selector,
            n_electrodes=n_electrodes, fs=fs, target_window=target_window,
            nfft=nfft, n_harmonics=n_harmonics, targets=targets,
            selected_channels=selected_channels)

    def eyeblink_detector(self, eog_channels=(7,), strategy="length",
                          rms_threshold=0):
        return self.decoder_factory.create_eyeblink_detector(eog_channels,
                                                             strategy,
                                                             rms_threshold)
    
    def template_match(self, buffering_decoder, threshold_decoder,
                       templates=None, n_electrodes=8,
                       selected_channels=None, reference_channel=None):
        return self.decoder_factory.create_template_match(
            templates, buffering_decoder, threshold_decoder, n_electrodes,
            selected_channels, reference_channel)

    def msequence_template_match(self, templates, n_electrodes=8, center=2,
                                 surround=(0, 4, 7), alpha=0.05,
                                 trial_marker=1, buffer_size=1000):
        return self.decoder_factory.create_msequence_template_match(
            templates, n_electrodes, center, surround, alpha, trial_marker,
            buffer_size)

    def vep_trial_logger(self, buffering_decoder, label='trial'):
        return self.decoder_factory.create_offline_vep_trial_recorder(
            buffering_decoder, label)

    def fixed_time_buffering_decoder(self, window_length=768, electrodes=8):
        return self.decoder_factory.create_fixed_time_buffering(
            window_length=window_length, electrodes=electrodes)

    def absolute_threshold_decoder(self, threshold, reduction_fn):
        reduction_fn = np.max
        return self.decoder_factory.create_absolute_threshold(
            threshold=threshold, reduction_fn=reduction_fn)

    def no_stimulation(self):
        canvas = self.controller_factory.create_canvas(self.window.width,
                                                       self.window.height)
        return Stimulation(canvas, UnlockState(True), [])

    ###########################################################################
    ## Applications
    ###########################################################################
    def experiment(self, stimulation=None, decoder=None, mode='test', block_sequence=(0,), trials_per_block=1,
                   offline_data=False):
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)
        normal_prop = CheckerboardProperties(180, 180, 1, 1, 1, 1, (255, 255, 255, 255), (0, 0, 0, 0))
        normal_models = list()
        normal_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, [1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,0,1,1]))
        normal_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, [0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1]))
        normal_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, [0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0]))
        normal_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, [0,1,0,1,1,1,1,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1,1,0,1,0,0,1,1,0]))

        normal_stimuli = self.state_factory.create_timed_stimuli(10.0, 0, *normal_models)
        normal_views = self.view_factory.create_quad_msequence_view(normal_models, stimulation.canvas, normal_prop)

        w = self.window.width
        h = self.window.height
        s = int(h / 10)
        x = int(w / s)
        y = int(h / s)
        overlap_props = list()
        alpha = 191
        overlap_props.append(CheckerboardProperties(x*s, y*s, x, y, 1, 1, (0, 255, 0, alpha), (0, 0, 0, 0)))
        overlap_props.append(CheckerboardProperties(x*s, y*s, x, y, 1, 1, (0, 0, 0, 0), (255, 0, 255, alpha)))

        overlap_models = list()
        overlap_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, [0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1]))
        overlap_models.append(self.state_factory.create_wall_clock_timed_stimulus(
            30.0, np.logical_not([0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0])))
        overlap_stimuli = self.state_factory.create_timed_stimuli(10.0, 0, *overlap_models)
        overlap_views = self.view_factory.create_dual_overlapping_cvep_view(
            overlap_models, stimulation.canvas, overlap_props)

        if not hasattr(self.signal, 'outlet'):
            class MockOutlet:
                def push_sample(self, x):
                    pass
            self.signal.outlet = MockOutlet()

        if mode == 'train':
            from unlock.state.experiment_state import ExperimentTrainerState
            model = ExperimentTrainerState(mode, normal_stimuli, overlap_stimuli, self.signal.outlet, decoder, block_sequence,
                                    trials_per_block)
            from unlock.view.experiment_view import ExperimentTrainerView
            view = ExperimentTrainerView(model, stimulation.canvas, normal_views, overlap_views)
        else:
            from unlock.state.experiment_state import ExperimentState
            model = ExperimentState(mode, normal_stimuli, overlap_stimuli, self.signal.outlet, decoder, block_sequence,
                                    trials_per_block)
            from unlock.view.experiment_view import ExperimentView
            view = ExperimentView(model, stimulation.canvas, normal_views, overlap_views)

        if offline_data:
            offline_data = self.state_factory.create_offline_data('experiment')
            state_chain = self.state_factory.create_state_chain(model, offline_data)
        else:
            state_chain = model

        # LSL hack
        normal_stimuli.outlet = self.signal.outlet
        overlap_stimuli.outlet = self.signal.outlet

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain, [view])

    def gridspeak(self, stimulation=None, decoder=None, grid_radius=2,
                  offline_data=False):
        assert stimulation and decoder
        #decoder.decoders[1].task_state = stimulation.stimuli.state
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)

        grid_state = self.state_factory.create_grid_hierarchy(grid_radius)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('gridspeak')
            state_chain = self.state_factory.create_state_chain(grid_state,
                                                                offline_data)
        else:
            state_chain = grid_state

        gridspeak_view = self.view_factory.create_gridspeak(grid_state,
                                                            stimulation.canvas)

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [gridspeak_view], name="Gridspeak", icon="gridspeak.png")

    def gridcursor(self, stimulation=None, decoder=None, grid_radius=2,
                   offline_data=False):
        assert stimulation and decoder

        #decoder.decoders[1].task_state = stimulation.stimuli.state
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)
        grid_state = self.state_factory.create_grid_hierarchy(grid_radius)

        if offline_data:
            offline_data = self.state_factory.create_offline_data('gridcursor')
            state_chain = self.state_factory.create_state_chain(grid_state,
                                                                offline_data)
        else:
            state_chain = grid_state

        grid_view = self.view_factory.create_hierarchy_grid_view(
            grid_state, stimulation.canvas)

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [grid_view], name="Target Practice", icon="gridcursor.png")

    def robot_controller(self, stimulation=None, decoder=None,
                         offline_data=False):
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)
        robot_state = self.state_factory.create_robot_controller()

        robot_view = self.view_factory.create_robot_controller_view(
            robot_state, stimulation.canvas)

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, robot_state,
            [robot_view], name="Robot Controller", icon="gridcursor.png")

    def robot(self, stimulation=None, decoder=None, grid_radius=1,
                   offline_data=False):
        assert stimulation and decoder

        #decoder.decoders[1].task_state = stimulation.stimuli.state
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)
        grid_state = self.state_factory.create_robot_grid(grid_radius)

        if offline_data:
            offline_data = self.state_factory.create_offline_data('gridspeak')
            state_chain = self.state_factory.create_state_chain(grid_state,
                                                                offline_data)
        else:
            state_chain = grid_state

        grid_view = self.view_factory.create_robot_grid_view(
            grid_state, stimulation.canvas)

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [grid_view], name="Target Practice", icon="gridcursor.png")


    def fastpad(self, stimulation=None, decoder=None, offline_data=False):
        assert stimulation and decoder
        decoder.decoders[1].task_state = stimulation.stimuli.state
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)

        fastpad_state = self.state_factory.create_fastpad()
        if offline_data:
            offline_data = self.state_factory.create_offline_data('fastpad')
            state_chain = self.state_factory.create_state_chain(fastpad_state,
                                                                offline_data)
        else:
            state_chain = fastpad_state

        fastpad_view = self.view_factory.create_fastpad_view(fastpad_state,
                                                             stimulation.canvas)
        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [fastpad_view], name="Fastpad", icon="fastpad.png")

    def time_scope(self, stimulation=None, channels=1, fs=256, duration=2,
                   offline_data=False):
        assert stimulation
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer}
        cmd_receiver = self.command_factory.create_receiver('raw',
                                                            **receiver_args)

        scope_model = TimeScopeState(channels, fs, duration)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('time_scope')
            state_chain = self.state_factory.create_state_chain(scope_model,
                                                                offline_data)
        else:
            state_chain = scope_model

        time_scope_view = TimeScopeView(scope_model, stimulation.canvas)
        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [time_scope_view], name='TimeScope', icon='time-128x128.jpg')

    def frequency_scope(self, stimulation=None, channels=1, fs=256, duration=2,
                        nfft=2048, freq_range=None, display_channels=None,
                        labels=None, margin=0.05, offline_data=False):
        assert stimulation
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer}
        cmd_receiver = self.command_factory.create_receiver('raw',
                                                            **receiver_args)

        scope_model = FrequencyScopeState(channels, fs, duration, nfft,
                                          freq_range, display_channels, labels)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('freq_scope')
            state_chain = self.state_factory.create_state_chain(scope_model,
                                                                offline_data)
        else:
            state_chain = scope_model

        frequency_scope_view = FrequencyScopeView(scope_model,
                                                  stimulation.canvas,
                                                  margin=margin,
                                                  labels=scope_model.labels)

        return self.controller_factory.create_controller_chain(
            self.window, stimulation, cmd_receiver, state_chain,
            [frequency_scope_view], name='FrequencyScope',
            icon='frequency2-128x128.png')

    def dashboard(self, stimulation=None, decoder=None, controllers=None,
                  offline_data=False):
        assert stimulation and decoder
        if not controllers:
            controllers = []
        #decoder.decoders[1].task_state = stimulation.stimuli.state
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer,
                         'decoder': decoder}
        cmd_receiver = self.command_factory.create_receiver('decoding',
                                                            **receiver_args)
        cc_frag = self.controller_factory.create_command_connected_fragment(
            stimulation.canvas, stimulation.stimuli, stimulation.views,
            cmd_receiver)

        icons = []
        for c in controllers:
            icons.append((c.icon_path, c.name))

        grid_state = self.state_factory.create_grid_state(controllers, icons)
        if offline_data:
            offline_data = self.state_factory.create_offline_data('dashboard')
            state_chain = self.state_factory.create_state_chain(grid_state,
                                                                offline_data)
        else:
            state_chain = grid_state

        grid_view = self.view_factory.create_grid_view(grid_state,
                                                       stimulation.canvas,
                                                       icons)
        return self.controller_factory.create_dashboard(
            self.window, stimulation.canvas, controllers, cc_frag, [grid_view],
            state_chain)

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

    def msequence_trainer(self, stimuli=None, decoder=None, sequences=None,
                          n_trials=None, trial_sequence=None, standalone=True,
                          position_sequence=None):
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer}
        if decoder:
            receiver_args['decoder'] = decoder
            cmd_receiver = self.command_factory.create_receiver(
                'decoding', **receiver_args)
        else:
            cmd_receiver = self.command_factory.create_receiver(
                'raw', **receiver_args)

        trainer = self.state_factory.create_msequence_trainer(
            stimuli, sequences, n_trials, trial_sequence, position_sequence)
        # super horrible hack
        decoder.decoders[0].task_state = trainer  # stimuli.stimuli.state
        decoder.decoders[-1].task_state = trainer

        cx, cy = stimuli.canvas.center()
        fixation = PygletTextLabel(UnlockState(True), stimuli.canvas, '+', cx, cy)
        aide = self.view_factory.create_image_sprite(UnlockState(True),
                                                     stimuli.canvas,
                                                     'obama.png', 0.25)
        stimuli.views.append(aide)

        return self.controller_factory.create_controller_chain(
            self.window, stimuli, cmd_receiver, trainer, [fixation],
            standalone=standalone)

    def ssvep_trainer(self, stimuli=None, decoder=None, frequencies=None,
                      n_trials=None, trial_sequence=None, standalone=True,
                      position_sequence=None):
        receiver_args = {'signal': self.signal,
                         'timer': self.acquisition_factory.timer}
        if decoder:
            receiver_args['decoder'] = decoder
            cmd_receiver = self.command_factory.create_receiver(
                'decoding', **receiver_args)
        else:
            cmd_receiver = self.command_factory.create_receiver(
                'raw', **receiver_args)

        trainer = self.state_factory.create_ssvep_trainer(
            stimuli, frequencies, n_trials, trial_sequence, position_sequence)
        # super horrible hack
        decoder.decoders[0].task_state = trainer  # stimuli.stimuli.state
        decoder.decoders[-1].task_state = trainer

        cx, cy = stimuli.canvas.center()
        fixation = PygletTextLabel(UnlockState(True), stimuli.canvas, '+', cx, cy)
        # fixation = self.view_factory.create_image_sprite(UnlockState(True),
        #                                                  stimuli.canvas,
        #                                                  'obama.png')

        return self.controller_factory.create_controller_chain(
            self.window, stimuli, cmd_receiver, trainer, [fixation],
            standalone=standalone)