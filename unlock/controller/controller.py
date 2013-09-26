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

from unlock.decode import PygletKeyboardCommand
import pyglet
import time


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
            
            
#class Graphic(object):
#    def __init__(self, x, y):
#        xs
   
class PygletWindow(pyglet.window.Window):
    def __init__(self, signal, fullscreen=False, show_fps=True, vsync=False):
        super(PygletWindow, self).__init__(fullscreen=fullscreen, vsync=vsync)
        self.signal = signal
        self.controller_stack = []
        self.views = []
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
        self.batch.draw()
        self.fps()
        
    def handle_stop_request(self):
        if self.active_controller:
            stop = self.active_controller.deactivate()
            if stop:
                self.signal.stop()
                self.signal.close()
                pyglet.app.exit()        
            return pyglet.event.EVENT_HANDLED
        else:
            self.signal.stop()
            self.signal.close()
            pyglet.app.exit()
            
            
    def activate_controller(self, controller):
        if self.active_controller:
            self.controller_stack.append(self.active_controller)
            pyglet.clock.unschedule(self.active_controller.poll_signal)            
            
        self.views = controller.get_views()
        self.batch = controller.get_batch()
        pyglet.clock.schedule_interval(controller.poll_signal, controller.get_signal_poll_freq())
        self.active_controller = controller
        
    def deactivate_controller(self):
        if self.active_controller != None:
            self.views = []        
            pyglet.clock.unschedule(self.active_controller.poll_signal)            
            self.active_controller = None
            
        if len(self.controller_stack) > 0:
            controller = self.controller_stack[-1]
            controller.activate()
            self.controller_stack = self.controller_stack[:-1]
            
    def start(self):
        pyglet.app.run()
            
            
class UnlockController(object):
    def __init__(self, window, views, canvas, signal_poll_freq=1.0/512.0):
        super(UnlockController, self).__init__()
        self.window = window
        self.views = views
        self.canvas = canvas
        self.signal_poll_freq = signal_poll_freq
        
    def activate(self):
        self.window.activate_controller(self)
        
    def render(self):
        self.window.render()
        
    def deactivate(self):
        return True
        
    def poll_signal(self, delta):
        pass
        
    def keyboard_input(self, command):
        pass
        
    def get_signal_poll_freq(self):
        return self.signal_poll_freq
        
    def get_views(self):
        return self.views
        
    def get_batch(self):
        return self.canvas.batch
            
            