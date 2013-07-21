from unlock.core import PygletKeyboardCommand
import pyglet
import time


class ScreenDescriptor(object):
    def __init__(self, batch, width, height):
        self.batch = batch
        self.width = width
        self.height = height
        
    @staticmethod
    def create(width, height):
        batch = pyglet.graphics.Batch()
        return ScreenDescriptor(batch, width, height)
            
            
class PygletController(pyglet.window.Window):
    def __init__(self, fullscreen=False, vsync=False, show_fps=False):
        super(PygletWindow, self).__init__(**{'fullscreen':fullscreen, 'vsync':vsync})
        self.views = []
        if show_fps:
            self.fps = pyglet.clock.ClockDisplay().draw
        else:
            def empty():
                pass
            self.fps = empty
        self.count = 0
        
        @self.event
        def on_draw():
            self.count += 1
            print "Draw... ", time.time()
            if self.count == 80:
                pyglet.app.exit()
                
            self.clear()
            for view in self.views:
                view.render() #Draws the apps to the screen
            self.fps()
                
        @self.event
        def on_key_press(symbol, modifiers):
            command = PygletKeyboardCommand(symbol, modifiers)
            if command.stop:
                stop = self.app.quit()
                if stop:
                    pyglet.app.exit()
            if command.decision or command.selection:
                self.app.keyboard_input(command)
                
    def set_app(self, app):
        self.app = app
        pyglet.clock.schedule_interval(app.poll_bci, 1.0/120.0)
            
    def add_view(self, view):
        self.views.append(view)
            
    def start(self):
        pyglet.app.run()
            
            
class UnlockController(PygletController):
    def __init__(self):
        pass
    def someshisit(self):
        pass
        
       