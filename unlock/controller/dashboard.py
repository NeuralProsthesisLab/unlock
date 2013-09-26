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
from unlock.decode import RawInlineSignalReceiver

from .controller import UnlockController, Canvas

import logging


class Dashboard(UnlockController):
    def __init__(self,window, views, canvas, timed_stimuli, grid_state, command_receiver):
        super(Dashboard, self).__init__(window, views, canvas)
        self.timed_stimuli = timed_stimuli
        self.grid_state = grid_state
        self.command_receiver = command_receiver
        self.logger = logging.getLogger(__name__)
        
    def __handle_command__(self, command):
        self.logger.debug('Dashboard.__handle_command__ delta, decision, selection = ', command.delta, command.decision, command.selection)
        self.grid_state.process_command(command)
        
    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        sequence_trigger = self.timed_stimuli.process_command(command)
        if sequence_trigger != Trigger.Null:
            command.set_sequence_trigger(sequence_trigger)
            
        self.__handle_command__(command)
        self.render()
        
    def activate(self):
        self.timed_stimuli.start()
        super(Dashboard, self).activate()
        
    def deactivate(self):
        self.command_receiver.stop()
        self.timed_stimuli.stop()
        self.window.deactivate_controller()
        return True
        
    def keyboard_input(self, command):
        self.__handle_command__(command)
        
    @staticmethod
    def create(window, controllers, signal, timer, stimulation_duration=4.0):
        if not controllers:
            raise ValueError
            
        canvas = Canvas.create(window.width, window.height)
        grid_state = GridState(controllers)
        command_receiver = RawInlineSignalReceiver(signal, timer)
        icons = []
        for controller in controllers:
            icons.append((controller.icon_path, controller.name))
            
        center_x, center_y = canvas.center()            
        grid_view = GridView(grid_state, canvas, icons, center_x, center_y)
        
        timed_stimuli = TimedStimuli.create(stimulation_duration)
        
        north_stimulus = TimedStimulus.create(30.0,  sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0))
        timed_stimuli.add_stimulus(north_stimulus)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(north_stimulus, canvas, SpritePositionComputer.North, width=200, height=200, xfreq=4, yfreq=4)
        
        east_stimulus = TimedStimulus.create(30.0, sequence=(0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0))
        timed_stimuli.add_stimulus(east_stimulus)            
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(east_stimulus, canvas, SpritePositionComputer.East, 90, width=200, height=200, xfreq=4, yfreq=4)
        
        south_stimulus = TimedStimulus.create(30.0, sequence=(0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1))
        timed_stimuli.add_stimulus(south_stimulus)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(south_stimulus, canvas, SpritePositionComputer.South, width=200, height=200, xfreq=4, yfreq=4)
        
        west_stimulus = TimedStimulus.create(30.0, sequence=(0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0))
        timed_stimuli.add_stimulus(west_stimulus)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(west_stimulus, canvas, SpritePositionComputer.West, 90, width=200, height=200, xfreq=4, yfreq=4)
        
        return Dashboard(window, [fs, fs1, fs2, fs3, grid_view], canvas, timed_stimuli, grid_state, command_receiver)
        
        