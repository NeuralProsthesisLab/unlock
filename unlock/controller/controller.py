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

from unlock.model import TimedStimulus, TimedStimuli
from unlock.view import FlickeringPygletSprite, SpritePositionComputer
from unlock.decode import UnlockClassifier, PygletKeyboardCommand, HarmonicSumDecision, RootMeanSquare
from unlock.decode import CommandReceiverFactory, RawInlineSignalReceiver,ClassifiedCommandReceiver
import pyglet
import inspect
import time
import os


class Canvas(object):
    def __init__(self, batch, width, height, xoffset=0, yoffset=0):
        self.batch = batch
        self.width = width
        self.height = height
        self.x = xoffset
        self.y = yoffset
        
    def center(self):
        return self.xcenter(), self.ycenter()
        
    def xcenter(self):
        return self.width / 2
    
    def ycenter(self):
        return self.height / 2
        
    @staticmethod
    def create(width, height, xoffset=0, yoffset=0):
        batch = pyglet.graphics.Batch()
        return Canvas(batch, width, height, xoffset, yoffset)
            
            
class PygletWindow(pyglet.window.Window):
    def __init__(self, decoder, fullscreen=False, show_fps=True, vsync=False):
        super(PygletWindow, self).__init__(fullscreen=fullscreen, vsync=vsync)
        self.decoder = decoder
        self.controller_stack = []
        self.views = []
        self.batches = set([])
        if show_fps:
            self.fps = pyglet.clock.ClockDisplay().draw
        else:
            def empty():
                pass
            self.fps = empty
        self.active_controller = None
        
        @self.event
        def on_key_press(symbol, modifiers):
            command = PygletKeyboardCommand(symbol, modifiers)
            if command.stop:
                return self.handle_stop_request()
            if self.active_controller and (command.decision or command.selection):
                self.active_controller.keyboard_input(command)
                
        @self.event
        def on_close():
            pass
            
    def render(self):
        self.clear()
        for view in self.views:
            view.render()
        for batch in self.batches:
            if batch != None:
                batch.draw()
        self.fps()
        
    def handle_stop_request(self):
        if self.active_controller:
            stop = self.active_controller.deactivate()
            if stop:
                self.decoder.shutdown()
                pyglet.app.exit()        
            return pyglet.event.EVENT_HANDLED
        else:
            self.decoder.shutdown()
            pyglet.app.exit()
            
            
    def activate_controller(self, controller):
        if self.active_controller:
            self.controller_stack.append(self.active_controller)
            pyglet.clock.unschedule(self.active_controller.poll_signal)            
            
        self.views = controller.views
        self.batches = controller.batches
        pyglet.clock.schedule(controller.poll_signal)#, controller.poll_signal_frequency)
        self.active_controller = controller
        
    def deactivate_controller(self):
        if self.active_controller != None:
            self.views = []
            self.batches = set([])
            pyglet.clock.unschedule(self.active_controller.poll_signal)
            self.active_controller = None
            
        if len(self.controller_stack) > 0:
            controller = self.controller_stack[-1]
            controller.activate()
            self.controller_stack = self.controller_stack[:-1]
            
    def start(self):
        pyglet.app.run()
            
            
class UnlockController(object):
    def __init__(self, window, views, batches, command_receiver, poll_signal_frequency,
                 standalone=False):
        super(UnlockController, self).__init__()
        self.window = window
        self.views = views
        self.batches = set([])
        if batches != None:
            self.batches = self.batches.union(batches)
            
        self.command_receiver = command_receiver
        self.standalone = standalone
        self.poll_signal_frequency = poll_signal_frequency
        
    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        self.update_state(command)
        self.render()
        
    def update_state(self, command):
        ''' Subclass hook '''
        pass
        
    def keyboard_input(self, command):
        self.update_state(command)
        self.render()
        
    def activate(self):
        self.window.activate_controller(self)
        
    def deactivate(self):
        return self.standalone
        
    def render(self):
        self.window.render()
        
        
class UnlockControllerChain(UnlockController):
    def __init__(self, window, command_receiver, controllers, name, icon,
                 poll_signal_frequency=1.0/512.0, standalone=False):
        assert controllers != None and len(controllers) > 0
        
        views = []
        batches = set([])
        for controller in controllers:
            if controller.views != None:
                views.extend(controller.views)    
                    
            if controller.batches != None:
                batches = batches.union(controller.batches)
                
        super(UnlockControllerChain, self).__init__(window, views, batches,
                                                    command_receiver, poll_signal_frequency,
                                                    standalone=standalone)
        self.controllers = controllers
        self.name = name
        self.icon = icon
        self.standalone = standalone
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(UnlockControllerChain)),
                                      'resource', self.icon)
        
    def update_state(self, command):
        for controller in self.controllers:
            controller.update_state(command)
        
    def keyboard_input(self, command):
        for controller in self.controllers:
            controller.keyboard_input(command)
        self.render()
        
    def activate(self):
        for controller in self.controllers:
            controller.activate()
        super(UnlockControllerChain, self).activate()
        
    def deactivate(self):
        for controller in self.controllers:
            controller.deactivate()
            
        self.window.deactivate_controller()            
        return self.standalone
        
    def render(self):
        super(UnlockControllerChain, self).render()
       
        
class UnlockControllerFragment(UnlockController):
    def __init__(self, model, views, batch, standalone=False):
        super(UnlockControllerFragment, self).__init__(None, None, None, None, None, None)
        self.model = model
        self.views = views
        self.batches.add(batch)
        self.standalone = standalone
        self.poll_signal = None
        self.render = None
        
    def update_state(self, command):
        if command.is_valid():
            self.model.process_command(command)
            
    def keyboard_input(self, command):
        self.model.process_command(command)
    
    def activate(self):
        self.model.start()
        
    def deactivate(self):
        self.model.stop()
        return self.standalone
            
          
class sEMGControllerFragment(UnlockControllerFragment):
    def __init__(self, command_receiver):
        super(sEMGControllerFragment, self).__init__(None, [], None)
        self.command_receiver = command_receiver
        
    def update_state(self, command):
        pass
        
    def keyboard_input(self, command):
        pass
        
    def activate(self):
        pass
        
    def deactivate(self):
        pass
        
    @staticmethod
    def create_semg(decoder, thresholds):
#        classifier = RootMeanSquare(thresholds)
        raise Exception("FML")
        #command_receiver = decoder.create_receiver(classifier=UnlockClassifierFactory.FacialEMGDetector,
        #                                           **{'thresholds' : thresholds })
        return sEMGControllerFragment(command_receiver)
        
        
class EEGControllerFragment(UnlockControllerFragment):
    def __init__(self, command_receiver, timed_stimuli, views, batch):
        assert timed_stimuli != None
        super(EEGControllerFragment, self).__init__(timed_stimuli, views, batch)
        self.command_receiver = command_receiver
        
    def update_state(self, command):
        return self.model.process_command(command)
        
    def keyboard_input(self,command):
        pass
        
    @staticmethod
    def create_ssvep(canvas, decoder, color='ry'):

        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)

        width = 200
        height = 200
        xf = 2
        yf = 2
        
        stimuli = TimedStimuli.create(4.0)
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
        args = {'targets' : freqs , 'duration': 4, 'fs': 256, 'electrodes':
            4 }
        command_receiver = decoder.create_receiver(args, classifier_type=UnlockClassifier.HarmonicSumDecision)
               
        return EEGControllerFragment(command_receiver, stimuli, views, canvas.batch)
        
        
    @staticmethod
    def create_msequence(canvas, signal, timer, color='bw'):
        raise Exception("This was not maintained through changes and needs some love before it is ready to run again..")
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
        
        command_receiver = RawInlineSignalReceiver(signal, timer)
        return EEGControllerFragment(command_receiver, stimuli, views, canvas.batch)
        
        