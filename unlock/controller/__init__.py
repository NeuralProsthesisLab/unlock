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
    TimedStimuli, OfflineTrialData, OfflineData, SequentialTimedStimuli, UnlockStateChain, UnlockStateFactory

from unlock.view import GridSpeakView, HierarchyGridView, FastPadView, GridView, FrequencyScopeView, \
    TimeScopeView, PygletDynamicTextLabel, PygletTextLabel, SpritePositionComputer, FlickeringPygletSprite, \
    UnlockViewFactory
    
from unlock.bci import UnlockCommandReceiverFactory, UnlockDecoder


class UnlockControllerFactory(object):
    """
    UnlockControllerFactory is the entry point for creating any externally accessible component
    of the controller package.
    """
    def __init__(self):
        super(UnlockControllerFactory, self).__init__()
        
    def create_canvas(width, height, xoffset=0, yoffset=0):        
        batch = pyglet.graphics.Batch()
        return Canvas(batch, width, height, xoffset, yoffset)
        
    def create_fastpad_fragment(canvas):
        fastpad_model = FastPadState()            
        fastpad_view = FastPadView(fastpad_model, canvas)
        assert canvas != None
        fastpad = UnlockControllerFragment(fastpad_model, [fastpad_view], canvas.batch)
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
            command_receiver = UnlockCommandReceiverFactory.create(UnlockCommandReceiverFactory.Raw,
                bci_wrapper.signal, bci_wrapper.timer)
        else:
            command_receiver = base.command_receiver
            
        controller_chain = UnlockControllerChain(window, command_receiver, [scope], 'FrequencyScope',
            'frequency-128x128.jpg', standalone=False)
        return controller_chain

    def create_command_connected_fragment(self, canvas, stimuli, command_receiver, color='bw'):

        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimuli,
            views, canvas.batch)
        return command_connected_fragment

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

    def create_dashboard(window, canvas, controllers, command_connected_fragment, calibrator=None):
        dashboard_fragment = UnlockControllerFactory.create_dashboard_fragment(window, canvas,
            controllers, calibrator)

        dashboard_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, dashboard_fragment], 'Dashboard', '', standalone=True)

        dashboard_fragment.poll_signal = dashboard_chain.poll_signal
        dashboard_chain.poll_signal = dashboard_fragment.poll_signal_interceptor
        return dashboard_chain

    def create_frame_count_timed_quad_ssvep_stimulation(canvas, color):
        UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color, UnlockStateFactory.create_frame_count_timed_stimulus)

    def create_wall_clock_timed_quad_ssvep_stimulation(canvas, color):
        UnlockControllerFactory.create_quad_ssvep_stimulation(canvas, color, UnlockStateFactory.create_wall_clock_timed_stimulus)

    def create_quad_ssvep_stimulation(canvas, color='bw', frequencies=[12.0, 13.0, 14.0, 15.0], stimuli_duration=3.0,
                                      rest_duration=1.0, width=500, height=100, xfrequency=5, yfrequency=1,
                                      timed_stimulus_factory_method=UnlockStateFactory.create_wall_clock_timed_stimulus):
        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)
        width = 500
        height = 100
        
        xfrequency = 5
        yfrequency = 1
        
        stimuli = UnlockStateFactory.create_timed_stimuli(stimuli_duration, rest_duration)
        views = []

        # XXX these should be injected
        stimulus = timed_stimulus_factory_method(frequencies[0] * 2)
        stimulus1 = timed_stimulus_factory_method(frequencies[1] * 2)
        stimulus2 = timed_stimulus_factory_method(frequencies[2] * 2)
        stimulus3 = timed_stimulus_factory_method(frequencies[3] * 2)

        stimuli.add_stimulus(stimulus)
        stimuli.add_stimulus(stimulus1)
        stimuli.add_stimulus(stimulus2)
        stimuli.add_stimulus(stimulus3)

        fs = UnlockViewFactory.create_flickering_checkered_box_sprite(stimulus, canvas,
            SpritePositionComputer.North, width=width, height=height, xfreq=xfrequency, yfreq=yfrequency,
            color_on=color1, color_off=color2, reversal=False)

        fs1 = UnlockViewFactory.create_flickering_checkered_box_sprite(stimulus, canvas,
            SpritePositionComputer.South, width=width, height=height, xfreq=xfrequency, yfreq=yfrequency,
            color_on=color1, color_off=color2, reversal=False)

        fs2 = UnlockViewFactory.create_flickering_checkered_box_sprite(stimulus, canvas,
            SpritePositionComputer.West, width=width, height=height, xfreq=xfrequency, yfreq=yfrequency,
            color_on=color1, color_off=color2, reversal=False, rotation=90)

        fs3 = UnlockViewFactory.create_flickering_checkered_box_sprite(stimulus3, canvas,
            SpritePositionComputer.East, width=width, height=height, xfreq=xfrequency, yfreq=yfrequency,
            color_on=color1, color_off=color2, reversal=False, rotation=90)

        views.append(fs)
        views.append(fs1)
        views.append(fs2)
        views.append(fs3)

        return stimuli, views

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
        
    def create_single_standalone_ssvep_diagnostic(window, command_receiver, output_file='collector',
            frequency=14.0, color=(255, 255, 0), color1=(255, 0, 0)):
         
        stimulus = UnlockStateFactory.create_wall_clock_timed_stimulus(frequency * 2)
        width = 300
        height = 300
        xfreq = 2
        yfreq = 2
        
        canvas = UnlockControllerFactory.create_canvas(window.height, window.width)
        fs = UnlockViewFactory.create_flickering_checkered_box_sprite(stimulus, canvas,
            SpritePositionComputer.Center, width=300, height=300, xfreq=2, yfreq=2, color_on=color,
            color_off=color1, reversal=False)
        views = [fs]
        
        offline_data = OfflineData(output_file)
        state = UnlockStateChain([stimulus, offline_data])
        
        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, state, views,
            canvas.batch)
            
        controller_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment], 'Collector', 'collector.png', standalone=True)
            
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
            
            