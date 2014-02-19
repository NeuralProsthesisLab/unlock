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
    
from unlock.bci import UnlockCommandFactory, UnlockDecoder



class UnlockControllerFactory(object):
    """
    UnlockControllerFactory is the entry point for creating any externally accessible component
    of the controller package.
    """
    def __init__(self):
        super(UnlockControllerFactory, self).__init__()

    def create_pyglet_window(self, signal, fullscreen=False, fps=True, vsync=True):
        return PygletWindow(signal, fullscreen, fps, vsync)

    def create_canvas(self, width, height, xoffset=0, yoffset=0):
        batch = pyglet.graphics.Batch()
        return Canvas(batch, width, height, xoffset, yoffset)

    def create_controller_chain(self, window, stimulation, command_receiver, state, views, name="Nameless",
            icon='', standalone=False):

        fragment = UnlockControllerFragment(state, views, stimulation.canvas.batch)
        command_connected_fragment = self.create_command_connected_fragment(stimulation.canvas, stimulation.stimuli,
            stimulation.views, command_receiver)

        chain = UnlockControllerChain(window, command_receiver, [command_connected_fragment, fragment], name, icon,
             standalone)

        return chain

    def create_command_connected_fragment(self, canvas, stimuli, views, command_receiver):
        command_connected_fragment = UnlockCommandConnectedFragment(command_receiver, stimuli, views, canvas.batch)
        return command_connected_fragment

    def create_dashboard(self, window, canvas, controllers, command_connected_fragment, views, state, calibrator=None):

        dashboard_fragment = UnlockDashboard(window, state, views, canvas.batch, controllers, calibrator)

        dashboard_chain = UnlockControllerChain(window, command_connected_fragment.command_receiver,
            [command_connected_fragment, dashboard_fragment], 'Dashboard', '', standalone=True)

        dashboard_fragment.poll_signal = dashboard_chain.poll_signal
        dashboard_chain.poll_signal = dashboard_fragment.poll_signal_interceptor
        return dashboard_chain

