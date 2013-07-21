from command import PygletKeyboardCommand
import pyglet
import time


class Canvas(object):
    def __init__(self, batch, width, height, xoffset=0, yoffset=0):
        self.batch = batch
        self.width = width
        self.height = height
        self.x = xoffset
        self.y = yoffset
        
    @staticmethod
    def create(width, height, xoffset=0, yoffset=0):
        batch = pyglet.graphics.Batch()
        return Canvas(batch, width, height)
            
            
#class Graphic(object):
#    def __init__(self, x, y):
#        xs
   
class PygletWindow(pyglet.window.Window):
    def __init__(self, fullscreen=False, vsync=False, show_fps=False):
        super(PygletWindow, self).__init__(fullscreen=fullscreen, vsync=vsync)
        self.views = []
        if show_fps:
            self.fps = pyglet.clock.ClockDisplay().draw
        else:
            def empty():
                pass
            self.fps = empty
        self.active_controller = None
        
        @self.event
        def on_draw():
            self.clear()
            for view in self.views:
                view.render()
            self.batch.draw()
            self.fps()
                
        @self.event
        def on_key_press(symbol, modifiers):
            command = PygletKeyboardCommand(symbol, modifiers)
            if command.stop and self.active_controller:
                stop = self.active_controller.quit()
                if stop:
                    pyglet.app.exit()
                    
            elif command.stop:
                pyglet.app.exit()
                
            if self.active_controller and (command.decision or command.selection):
                self.active_controller.keyboard_input(command)
                
    def set_active_controller(self, controller):
        self.views = controller.get_views()
        self.batch = controller.get_batch()
        pyglet.clock.schedule_interval(controller.poll_bci, controller.get_bci_poll_freq())
        self.active_controller = controller
        
    def start(self):
        pyglet.app.run()
            
            
class UnlockController(object):
    def __init__(self, window, views, canvas, bci_poll_freq=1.0/120.0):
        super(UnlockController, self).__init__()
        self.window = window
        self.views = views
        self.canvas = canvas
        self.bci_poll_freq = bci_poll_freq

    def make_active(self):
        self.window.set_active_controller(self)
        
    def poll_bci(self, command):
        pass
        
    def get_bci_poll_freq(self):
        return self.bci_poll_freq
        
    def get_views(self):
        return self.views
        
    def get_batch(self):
        return self.canvas.batch
        
    def quit(self):
        return True
            
            