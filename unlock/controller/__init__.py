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
from unlock.controller.controller import *

from unlock.state import HierarchyGridState, FastPadState, ControllerGridState, FrequencyScopeState, \
    TimeScopeState, ContinuousVepDiagnosticState, DiscreteVepDiagnosticState, TimedStimulus, \
    TimedStimuli, OfflineTrialData, OfflineData, SequentialTimedStimuli, UnlockStateChain

from unlock.view import GridSpeakView, HierarchyGridView, FastPadView, GridView, FrequencyScopeView, \
    TimeScopeView, PygletDynamicTextLabel, PygletTextLabel, SpritePositionComputer, FlickeringPygletSprite
    
from unlock.bci import UnlockCommandReceiverFactory, UnlockDecoder


class UnlockControllerFactory(object):
    """
    UnlockControllerFactory is the entry point for creating any externally accessible component
    of the controller package.
    """
    def __init__(self):
        super(ControllerFactory, self).__init__()
        
    def create_canvas(width, height, xoffset=0, yoffset=0):        
        batch = pyglet.graphics.Batch()
        return Canvas(batch, width, height, xoffset, yoffset)
        
    def create_fastpad_fragment(canvas):
        fastpad_model = FastPadState()            
        fastpad_view = FastPadView(fastpad_model, canvas)
        assert canvas != None
        fastpad = FastPad(fastpad_model, [fastpad_view], canvas.batch)        
        return fastpad
        
    def create_fastpad(window, bci_wrapper, base=None, color='bw'):
        canvas = Canvas.create(window.width, window.height)
        if base == None:
            base = UnlockControllerFactory.create_quad_ssvep(canvas,
                bci_wrapper, color)
            
        assert base != None
        fastpad = UnlockControllerFactory.create_fastpad_fragment(canvas)
        controller_chain = UnlockControllerChain(window, base.command_receiver, [base, fastpad],
            'FastPad', 'fastpad.png', standalone=False)
        return controller_chain
        
    def create_time_scope_fragment(canvas, n_channels=1, fs=256, duration=2):
        scope_model = TimeScopeState(**kwargs)
        scope_view = TimeScopeView(scope_model, canvas)
        assert canvas is not None
        scope = UnlockControllerFragment(scope_model, [scope_view], canvas.batch)
        return scope
        
    def create_time_scope(window, bci_wrapper, base=None, **kwargs):
        canvas = Canvas.create(window.width, window.height)        
        scope = TimeScope.create_time_scope_fragment(canvas, **kwargs)
        if base is None:
            command_receiver = CommandReceiverFactory.create(
                CommandReceiverFactory.Raw, bci_wrapper.signal, bci_wrapper.timer)
        else:
            command_receiver = base.command_receiver
            
        controller_chain = UnlockControllerChain(window, command_receiver, [scope], 'TimeScope',
            'time-128x128.jpg', standalone=False)
        return controller_chain
        
    def create_frequency_scope_fragment(canvas, **kwargs):
        scope_model = FrequencyScopeState(**kwargs)
        scope_view = FrequencyScopeView(scope_model, canvas, labels=scope_model.labels)
        assert canvas is not None
        scope = UnlockControllerFragment(scope_model, [scope_view], canvas.batch)
        return scope
        
    def create_frequency_scope(window, bci_wrapper, base=None, **kwargs):
        canvas = Canvas.create(window.width, window.height)
        scope = UnlockControllerFragment.create_frequency_scope_fragment(canvas, **kwargs)
        if base is None:
            command_receiver = CommandReceiverFactory.create(CommandReceiverFactory.Raw,
                bci_wrapper.signal, bci_wrapper.timer)
        else:
            command_receiver = base.command_receiver
            
        controller_chain = UnlockControllerChain(window, command_receiver, [scope], 'FrequencyScope',
            'frequency-128x128.jpg', standalone=False)
        return controller_chain
        
    def create_dashboard_fragment(window, canvas, controllers, calibrator):      
        grid_state = ControllerGridState(controllers)
        icons = []
        for controller in controllers:
            icons.append((controller.icon_path, controller.name))
            
        center_x, center_y = canvas.center()
        grid_view = GridView(grid_state, canvas, icons, center_x, center_y)
        offline_data = OfflineData("dashboard")        
        state = UnlockStateChain([grid_state, offline_data])
        
        return UnlockDashboard(window, state, [grid_view], canvas.batch, controllers, calibrator)
        
    def create_quad_ssvep_stimulation(canvas, color):
        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)
        width = 500
        height = 100
        
        xf = 5
        yf = 1
        
        stimuli = TimedStimuli.create(3.0, 1.0)
        views = []
        
        freqs = [12.0, 13.0, 14.0, 15.0]
        
        stimulus1 = TimedStimulus.create(freqs[0] * 2)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False)
        stimuli.add_stimulus(stimulus1)
        views.append(fs1)
        
        stimulus2 = TimedStimulus.create(freqs[1] * 2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False)
        stimuli.add_stimulus(stimulus2)
        views.append(fs2)
        
        stimulus3 = TimedStimulus.create(freqs[2] * 2)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False, rotation=90)
        stimuli.add_stimulus(stimulus3)
        views.append(fs3)
        
        stimulus4 = TimedStimulus.create(freqs[3] * 2)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
             reversal=False, rotation=90)
        stimuli.add_stimulus(stimulus4)
        views.append(fs4)
        return stimuli, views
        
    def create_dashboard(window, controllers, command_receiver, calibrator=None, color='bw'):        
        canvas = UnlockControllerFactory.create_canvas(window.width, window.height)
        dashboard_fragment = UnlockControllerFactory.create_dashboard_fragment(window, canvas,
            controllers, calibrator)
            
        stimuli, views = UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color)        
        
        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimuli,
            views, canvas.batch)
            
        dashboard_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, dashboard_fragment], 'Dashboard', '', standalone=True)
            
        dashboard_fragment.poll_signal = dashboard_chain.poll_signal
        dashboard_chain.poll_signal = dashboard_fragment.poll_signal_interceptor
        return dashboard_chain
        
    def create_gridspeak_fragment(canvas):
        grid_model = HierarchyGridState(2)
        gridspeak_view = GridSpeakView(None, grid_model, canvas)
        assert canvas != None
        offline_data = OfflineData("gridspeak")        
        state = UnlockStateChain([grid_model, offline_data])
        gridspeak = UnlockControllerFragment(state, [gridspeak_view], canvas.batch)
        return gridspeak
        
    def create_gridspeak(window, command_receiver, color='bw'):
        canvas = UnlockControllerFactory.create_canvas(window.width, window.height)
        gridspeak_fragment = UnlockControllerFactory.create_gridspeak_fragment(canvas)
            
        stimuli, views = UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color)        
        
        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimuli,
            views, canvas.batch)
            
        gridspeak_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, gridspeak_fragment], 'Gridspeak', 'gridspeak.png', standalone=False)
            
        return gridspeak_chain
        
    def create_gridcursor_fragment(canvas):
        grid_model = HierarchyGridState(2)
        grid_view = HierarchyGridView(grid_model, canvas)
        assert canvas != None
        offline_data = OfflineData("gridcursor")        
        state = UnlockStateChain([grid_model, offline_data])
        gridcursor = UnlockControllerFragment(state, [grid_view], canvas.batch)
        return gridcursor
        
    def create_gridcursor(window, command_receiver, color='bw'):
        canvas = UnlockControllerFactory.create_canvas(window.width, window.height)
        gridcursor_fragment = UnlockControllerFactory.create_gridcursor_fragment(canvas)
            
        stimuli, views = UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color)        
        
        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimuli,
            views, canvas.batch)
            
        gridcursor_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, gridcursor_fragment], 'Gridcursor', 'gridcursor.png', standalone=False)
            
        return gridcursor_chain        
        
    def create_diagnostic(window, bci_wrapper, **kwargs):
        print ("kwargs = ", kwargs)
            
        canvas = UnlockControllerFactory.create_canvas(window.width, window.height)
#        stimuli = UnlockControllerFactory.create_single_ssvep(canvas, command_receiver, 10.0, **kwargs['stimulus'])
#        controllers.append(stimuli)
                
#        hsd = new_fixed_time_threshold_hsd(**kwargs)
#        diagnostic = Diagnostic.create_vep_diagnostic_fragment(diagnostic_canvas, scope, stimuli,
#            bci_wrappers, kwargs['diagnostic'])
#        controllers.append(diagnostic)
            
        controller_chain = UnlockControllerChain(window, command_receiver, controllers,
            'Diagnostic', 'frequency2-128x128.png', standalone=False)
        return controller_chain
        
    def create_quad_ssvep(canvas, bci_wrapper, color='bw'):
        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)
        width = 500
        height = 100

        xf = 5
        yf = 1
        
        stimuli = TimedStimuli.create(3.0, 1.0)
        views = []
        
        freqs = [12.0, 13.0, 14.0, 15.0]
        
        stimulus1 = TimedStimulus.create(freqs[0] * 2)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False)
        stimuli.add_stimulus(stimulus1)
        views.append(fs1)
        
        stimulus2 = TimedStimulus.create(freqs[1] * 2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False)
        stimuli.add_stimulus(stimulus2)
        views.append(fs2)
        
        stimulus3 = TimedStimulus.create(freqs[2] * 2)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
            reversal=False, rotation=90)
        stimuli.add_stimulus(stimulus3)
        views.append(fs3)
        
        stimulus4 = TimedStimulus.create(freqs[3] * 2)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=width,
            height=height, xfreq=xf, yfreq=yf, color_on=color1,
            color_off=color2,
             reversal=False, rotation=90)
        stimuli.add_stimulus(stimulus4)
        views.append(fs4)

        # XXX: this should be passed in, not pulled out
        task_state = stimuli.state

        args = {'task_state': task_state, 'targets': freqs, 'trial_length': 3,
                'fs': 256, 'n_electrodes': 8}
        ssvep_command_receiver = bci_wrapper.create_receiver(args,
            decoder_type=UnlockDecoder.HarmonicSumDecision)

        eb_args = {'task_state': task_state, 'eog_channels': [4],
                   'strategy': 'count', 'rms_threshold': 4000}
        command_receiver = bci_wrapper.create_receiver(eb_args,
            decoder_type=UnlockDecoder.EyeBlinkDetector,
            chained_decoder=ssvep_command_receiver)
        
        return UnlockCommandConnectedFragment(command_receiver, stimuli, views, canvas.batch)
        
    def create_single_standalone_ssvep_diagnostic(window, command_receiver, output_file='collector',
        frequency=14.0, color=(255, 255, 0), color1=(255, 0, 0)):
                 
        stimulus = TimedStimulus.create(frequency * 2)    
        width = 300
        height = 300
        xfreq = 2
        yfreq = 2

        canvas = UnlockControllerFactory.create_canvas(window.height, window.width)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(stimulus, canvas,
            SpritePositionComputer.Center, width=300, height=300, xfreq=2, yfreq=2, color_on=color,
            color_off=color1, reversal=False)
        views = [fs]

        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimulus,
            views, canvas.batch)
            
        offline_data = OfflineData(output_file)
        
        collector = UnlockControllerFragment(offline_data, [], None)
        
        def keyboard_input(self, command):
            pass    
        collector.keyboard_input = keyboard_input
        
        controller_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, collector], 'Collector', 'collector.png', standalone=True)
            
        return controller_chain
        
    def create_eeg_emg_collector(window, bci_wrapper, stimuli=None, trials=10, cue_duration=.5,
                         rest_duration=1, indicate_duration=1, output_file='collector', standalone=False):
        raise Exception("Old code that is no longer supported")
        canvas = Canvas.create(window.width, window.height)
        cues = [Trigger.Left, Trigger.Right, Trigger.Up, Trigger.Down, Trigger.Select]
        cue_states = []
        for cue in cues:  
            cue_states.append(CueState.create(cue, cue_duration))
                              
        rest_state = CueState.create(Trigger.Rest, rest_duration)

        indicate_state = DynamicPositionCueState.create(Trigger.Indicate, indicate_duration, canvas.height, canvas.height/8,
                                              canvas.width, canvas.width/8)
        
        cue_state = CueStateMachine.create_sequential_cue_indicate_rest(cue_states, rest_state,
                                                                        indicate_state,trials=trials)
        
        left = PygletTextLabel(cue_state.cue_states[0], canvas, 'left', canvas.width / 2.0,
                               canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0,
                                canvas.height / 2.0)
        forward = PygletTextLabel(cue_state.cue_states[2], canvas, 'up', canvas.width / 2.0,
                                  canvas.height / 2.0)
        back = PygletTextLabel(cue_state.cue_states[3], canvas, 'down', canvas.width / 2.0,
                               canvas.height / 2.0)
        select = PygletTextLabel(cue_state.cue_states[4], canvas, 'select', canvas.width / 2.0,
                                 canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)
        
        indicate_text = DynamicPositionPygletTextLabel(cue_state.indicate_state, canvas, '+',
                                                       canvas.width / 2.0, canvas.height / 2.0)
        
        offline_data = OfflineData(output_file)
        collector = Collector(window, cue_state, offline_data, [left, right, forward, back, select, rest, indicate_text],
                              canvas.batch, standalone=standalone)
        view_chain = collector.views
        
        command_receiver = RawInlineSignalReceiver(bci_wrapper.signal, bci_wrapper.timer)
        
        controller_chain = UnlockControllerChain(window, command_receiver,
                                                 [collector] , 'Collector', 'collector.png',
                                                 standalone=standalone)
        return controller_chain
            
    def create_facial_emg_collector(window, bci_wrapper, stimuli=None, trials=10, cue_duration=.5,
                         rest_duration=1, indicate_duration=1, output_file='collector', standalone=False):
        raise Exception("Old code that is no longer supported")        
        canvas = Canvas.create(window.width, window.height)
        cues = [Trigger.Left, Trigger.Right, Trigger.Forward, Trigger.Back, Trigger.Select]
        cue_states = []
        for cue in cues:  
            cue_states.append(CueState.create(cue, cue_duration))
                              
        rest_state = CueState.create(Trigger.Rest, rest_duration)

        indicate_state = CueState.create(Trigger.Indicate, indicate_duration)
        
        cue_state = CueStateMachine.create_sequential_cue_indicate_rest(cue_states, rest_state,
                                                                        indicate_state,trials=trials)
        
        left = PygletTextLabel(cue_state.cue_states[0], canvas, 'left', canvas.width / 2.0,
                               canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0,
                                canvas.height / 2.0)
        forward = PygletTextLabel(cue_state.cue_states[2], canvas, 'forward', canvas.width / 2.0,
                                  canvas.height / 2.0)
        back = PygletTextLabel(cue_state.cue_states[3], canvas, 'back', canvas.width / 2.0,
                               canvas.height / 2.0)
        select = PygletTextLabel(cue_state.cue_states[4], canvas, 'select', canvas.width / 2.0,
                                 canvas.height / 2.0)
        
        rest = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
#        rest = BellRingTextLabelDecorator(rest_text)
        
        indicate_text = BellRingTextLabelDecorator(PygletTextLabel(cue_state.indicate_state, canvas, '',
                                       canvas.width / 2.0, canvas.height / 2.0))
        
        offline_data = OfflineData(output_file)
        collector = Collector(window, cue_state, offline_data, [left, right, forward, back, select, rest, indicate_text],
                              canvas.batch, standalone=standalone)
        view_chain = collector.views
        
        command_receiver = RawInlineSignalReceiver(bci_wrapper.signal, bci_wrapper.timer)
        
        controller_chain = UnlockControllerChain(window, command_receiver,
                                                 [collector] , 'Collector', 'collector.png',
                                                 standalone=standalone)
        return controller_chain
            
    def create_calibration_fragment(window, command_receiver, trials=4, cue_duration=.5,
        rest_duration=1, indicate_duration=1, standalone=False):
        
        raise Exception("Old code that is no longer supported")        
        canvas = Canvas.create(window.width, window.height)
        cues = [Trigger.Left, Trigger.Right, Trigger.Forward, Trigger.Select]
        cue_states = []
        for cue in cues:
            cue_states.append(CueState.create(cue, cue_duration))
        rest_state = CueState.create(Trigger.Rest, rest_duration)

        indicate_state = CueState.create(Trigger.Indicate, indicate_duration)        
        cue_state = CueStateMachine.create_sequential_cue_indicate_rest(cue_states, rest_state,
                                                                        indicate_state,trials=trials)
        
        left = PygletTextLabel(cue_state.cue_states[0], canvas, 'left', canvas.width / 2.0,
                               canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0,
                                canvas.height / 2.0)
        forward = PygletTextLabel(cue_state.cue_states[2], canvas, 'forward', canvas.width / 2.0,
                                  canvas.height / 2.0)
#        back = PygletTextLabel(cue_state.cue_states[3], canvas, 'back', canvas.width / 2.0,
 #                              canvas.height / 2.0)
        select = PygletTextLabel(cue_state.cue_states[3], canvas, 'select', canvas.width / 2.0,
                                 canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0,
                                    canvas.height / 2.0)
        
        
        indicate_text = PygletTextLabel(cue_state.indicate_state, canvas, '',
                                                       canvas.width / 2.0, canvas.height / 2.0)
        indicate = BellRingTextLabelDecorator(indicate_text)
        
        calibrate = Calibrate(window, command_receiver.classifier, cue_state, [left, right, forward, select, rest_text, indicate],
                              canvas.batch)
        view_chain = calibrate.views
        controller_chain = UnlockControllerChain(window, command_receiver.command_receiver,
                                                 [calibrate], 'Calibrate', 'scope.png',
                                                 standalone=standalone)
        return calibrate, controller_chain
            
            