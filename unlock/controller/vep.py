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

from unlock.model import TimedStimulus, HierarchyGridState, TimedStimuli, OfflineData
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, HierarchyGridView
from unlock.decode import HarmonicSumDecision, RawInlineSignalReceiver, ClassifiedCommandReceiver
from unlock.controller import UnlockController, Canvas
import inspect
import os


class VEP(UnlockController):
    def __init__(self, window, views, canvas, command_receiver, timed_stimuli,
                 grid_state, recorder, icon="LazerToggleS.png",
                 name="VEP"):
        assert command_receiver != None and timed_stimuli != None and grid_state != None and recorder != None
        super(VEP, self).__init__(window, views, canvas)
        self.command_receiver = command_receiver
        self.timed_stimuli = timed_stimuli
        self.grid_state = grid_state
        self.recorder = recorder
        self.name = name
        self.icon = icon
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(VEP)),
                                      'resource', self.icon)
        
    def __handle_command__(self, command):
        self.grid_state.process_command(command)
        
    def keyboard_input(self, command):
        self.__handle_command__(command)
        
    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        self.update_state(command)
        
    def update_state(self, command):
        self.timed_stimuli.process_command(command)
        if command.is_valid():
            self.recorder.process_command(command)
        self.__handle_command__(command)
        self.render()        
        
    def activate(self):
        self.timed_stimuli.start()
        self.recorder.start()
        super(VEP, self).activate()
        
    def deactivate(self):
        self.command_receiver.stop()
        self.timed_stimuli.stop()
        self.recorder.stop()
        self.window.deactivate_controller()
        return False
        
    @staticmethod
    def create_ssvep(window, signal, timer, color='bw'):
        canvas = Canvas.create(window.width, window.height)
        
        if color == 'bw':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)
        
        stimuli = TimedStimuli.create(4.0)
        views = []
        
        freqs = [12.0, 13.0, 14.0, 15.0]
        
        stimulus1 = TimedStimulus.create(freqs[0] * 2)
        # fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
        #     stimulus1, canvas, SpritePositionComputer.North, width=500,
        #     height=100, xfreq=5, yfreq=1, color_on=color1, color_off=color2,
        #     reversal=False)
        #stimuli.append(stimulus1)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=200,
            height=200, xfreq=2, yfreq=2, color_on=color1, color_off=color2,
            reversal=False)
        stimuli.add_stimulus(stimulus1)
        views.append(fs1)
        
        stimulus2 = TimedStimulus.create(freqs[1] * 2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=200,
            height=200, xfreq=2, yfreq=2, color_on=color1, color_off=color2,
            reversal=False)
        #stimuli.append(stimulus2)
        stimuli.add_stimulus(stimulus2)
        views.append(fs2)
        
        stimulus3 = TimedStimulus.create(freqs[2] * 2)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=200,
            height=200, xfreq=2, yfreq=2, color_on=color1, color_off=color2,
            xoffset=350, reversal=False)
        #stimuli.append(stimulus3)
        stimuli.add_stimulus(stimulus3)
        views.append(fs3)
        
        stimulus4 = TimedStimulus.create(freqs[3] * 2)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=200,
            height=200, xfreq=2, yfreq=2, color_on=color1, color_off=color2,
            xoffset=-350, reversal=False)
        #stimuli.append(stimulus4)
        stimuli.add_stimulus(stimulus4)
        views.append(fs4)
        
        grid_model = HierarchyGridState(2)
        grid = HierarchyGridView(grid_model, canvas)
        views.append(grid)
        
        recorder = OfflineData('ssvep')
        
        raw_command_receiver = RawInlineSignalReceiver(signal, timer)
        classifier = HarmonicSumDecision(freqs, 3.0, 500, 8)
        command_receiver = ClassifiedCommandReceiver(raw_command_receiver, classifier)
        
        return VEP(window, views, canvas, command_receiver, stimuli,
                   grid_model, recorder, name='SSVEP')
            
    @staticmethod
    def create_msequence(window, signal, timer, color='bw'):
        canvas = Canvas.create(window.width, window.height)
        
        rate = 30.0
        width = 300
        height = 300
        fx = 4
        fy = 4
        
        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (255, 255, 255)
            color2 = (0, 0, 0)
        
        seq1 = (1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,0,1,1)
        seq2 = (0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1)
        seq3 = (0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0)
        seq4 = (0,1,0,1,1,1,1,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1,1,0,1,0,0,1,1,0)
        
        stimuli = TimedStimuli.create(4.0)
        views = []
        
        stimulus1 = TimedStimulus.create(rate, sequence=seq1)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.add_stimulus(stimulus1)
        views.append(fs1)
        
        stimulus2 = TimedStimulus.create(rate, sequence=seq2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.add_stimulus(stimulus2)
        views.append(fs2)
        
        stimulus3 = TimedStimulus.create(rate, sequence=seq3)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.add_stimulus(stimulus3)
        views.append(fs3)
        
        stimulus4 = TimedStimulus.create(rate, sequence=seq4)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.add_stimulus(stimulus4)
        views.append(fs4)
        
        grid_model = HierarchyGridState(2)
        grid = HierarchyGridView(grid_model, canvas)
        views.append(grid)
        
        recorder = OfflineData('msequence')
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        return VEP(window, views, canvas, command_receiver, stimuli,
                   grid_model, recorder, "emg-100x100.jpg", name='cVEP')
            
            