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

from unlock.model import GridState, TimedStimuli, TimedStimulus
from unlock.util import Trigger
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, GridView
from unlock.decode import RawInlineSignalReceiver, CommandReceiverFactory
from .controller import UnlockControllerChain, Canvas, UnlockControllerFragment, EEGControllerFragment
import logging


class Dashboard(UnlockControllerFragment):
    def __init__(self, window, model, views, batch, controllers, calibrator):
        super(Dashboard, self).__init__(model, views, batch)
        self.window = window
        self.controllers = controllers
        self.calibrator = calibrator
        if calibrator != None:
            self.initialized = False
        else:
            self.initialized = True
            
        self.logger = logging.getLogger(__name__)

    def initialize(self):
        for controller in self.controllers:
            for fragment in controller.controllers:
                if fragment == self.calibrator:
                    controller.activate()
                    
        self.initialized = True
        
    def poll_signal_interceptor(self, delta):
        if not self.initialized:
            self.initialize()
            return
        self.poll_signal(delta)
            
    @staticmethod
    def create_dashboard_fragment(window, canvas, controllers, calibrator):
        if not controllers:
            raise ValueError
            
        grid_state = GridState(controllers)
        icons = []
        for controller in controllers:
            icons.append((controller.icon_path, controller.name))
            
        center_x, center_y = canvas.center()            
        grid_view = GridView(grid_state, canvas, icons, center_x, center_y)
        
        return Dashboard(window, grid_state, [grid_view], canvas.batch, controllers, calibrator)
        
    @staticmethod
    def create_dashboard(window, controllers, signal, timer, base=None, calibrator=None, color='bw', receiver_type=CommandReceiverFactory.Classified):
        canvas = Canvas.create(window.width, window.height)
        if base == None:
            base = EEGControllerFragment.create_ssvep(canvas, signal, timer, color, receiver_type=receiver_type)
            
        dashboard = Dashboard.create_dashboard_fragment(window, canvas, controllers, calibrator)
        dashboard_chain = UnlockControllerChain(window, base.command_receiver,
                                                 [base, dashboard] , 'Dashboard', '',
                                                 standalone=True)
        dashboard.poll_signal = dashboard_chain.poll_signal
        dashboard_chain.poll_signal = dashboard.poll_signal_interceptor
        return dashboard_chain
        
        