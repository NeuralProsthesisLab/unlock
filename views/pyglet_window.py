import pyglet
from unlock.core import PygletKeyboardCommand
#import controller
#from unlock.util import 

class ScreenDescriptor(object):
    def __init__(self, batch, width, height):
        self.batch = batch
        self.width = width
        self.height = height
    @staticmethod
    def create(width, height):
        batch = pyglet.graphics.Batch()
        return ScreenDescriptor(batch, width, height)
    
class App(object):
    def __init__(self):
        pass
    def quit(self):
        print ' quit'
        return True
    def keyboard_input(self, command):
        print "keypbaord inpute "
    def poll_bci(self, delta):
        #print "poll bci ", delta     
        pass 
class PygletWindow(pyglet.window.Window):
    def __init__(self, fullscreen=False, vsync=False, show_fps=False):
        super(PygletWindow, self).__init__(**{'fullscreen':fullscreen, 'vsync':vsync})
        self.views = []
        self.show_fps = show_fps
        self.fps = pyglet.clock.ClockDisplay()
            
        @self.event
        def on_draw():
            self.clear()
            for view in self.views:
                view.render() #Draws the apps to the screen
                
            if self.show_fps:
                self.fps.draw() #FPS Timer
                
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
        pyglet.clock.schedule(app.poll_bci)
        
    def add_view(self, view):
        self.views.append(view)
            
    def start(self):
        pyglet.app.run()
            
          