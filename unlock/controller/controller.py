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

from unlock.bci import PygletKeyboardCommand
import logging
import pyglet
import inspect
import time
import os


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
        #print("TYPE COMMAND = ", type(command#))
        
        if 'stop' in command.__dict__:
            self.window.handle_stop_request()
        else:
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
        self.window.deactivate_controller()
        return self.standalone
        
    def render(self):
        #print("Render =======================================================================")
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
            command_receiver, poll_signal_frequency, standalone=standalone)
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
    """
    A controller fragment is a controller that can be 'mixedin' with other fragments.  It is not
    intended to be a stand alone controller.  For a stand alone controller use/subclass
    UnlockController or UnlockControllerChain.
    """
    def __init__(self, model, views, batch, check_command_validity=False):
        super(UnlockControllerFragment, self).__init__(None, None, None, None, None, None)
        self.model = model
        self.views = views
        self.batches.add(batch)
        self.check_command_validity = check_command_validity
        self.poll_signal = None
        self.render = None
        
    def update_state(self, command):
        if command is not None and self.model is not None:
            if self.check_command_validity and not command.is_valid():
                return
                
            self.model.process_command(command)
            
    def keyboard_input(self, command):
        if self.model is not None:
            self.model.process_command(command)
            
    def activate(self):
        if self.model is not None:
            self.model.start()
            
    def deactivate(self):
        if self.model is not None:
            self.model.stop()
        return self.standalone
         
            
class UnlockCommandConnectedFragment(UnlockControllerFragment):
    def __init__(self, command_receiver, timed_stimuli, views, batch):
        assert timed_stimuli is not None
        super(UnlockCommandConnectedFragment, self).__init__(timed_stimuli, views, batch)
        self.command_receiver = command_receiver
        
    def keyboard_input(self,command):
        pass
        
    def activate(self):
        assert self.command_receiver != None
        super(UnlockCommandConnectedFragment, self).activate()
        self.command_receiver.start()
        
    def deactivate(self):
        assert self.command_receiver != None        
        self.command_receiver.stop()
        super(UnlockCommandConnectedFragment, self).deactivate()
        
        
class UnlockCalibratedControllerFragment(UnlockControllerFragment):
    def __init__(self, window, model, views, batch, calibrator=None):
        super(UnlockCalibratedControllerFragment, self).__init__(model, views, batch)
        self.window = window
        self.calibrator = calibrator
        if calibrator != None:
            self.initialized = False
        else:
            self.initialized = True            
            
    def initialize(self):
        self.calibrator.activate()
        self.initialized = True
        
    def poll_signal_interceptor(self, delta):
        if not self.initialized:
            self.initialize()
            return
        self.poll_signal(delta)
        
        
class UnlockDashboard(UnlockCalibratedControllerFragment):
    def __init__(self, window, model, views, batch, controllers, calibrator):
        super(UnlockDashboard, self).__init__(window, model, views, batch, calibrator)
        self.controllers = controllers
        self.logger = logging.getLogger(__name__)
        
        
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
        return self.width / 2 + self.x
        
    def ycenter(self):
        return self.height / 2 + self.y
            
          
