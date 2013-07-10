import pyglet
from unlock.command import Command
#import controller
#from unlock.util import 

class PygletWindow(pyglet.window.Window):
    def __init__(self, view, controller, fullscreen=False, vsync=False, show_fps=False):
        super(PygletWindow, self).__init__(**{'fullscreen':fullscreen, 'vsync':vsync})
        self.view = view
        self.controller = controller
        self.show_fps = show_fps
        self.fps = pyglet.clock.ClockDisplay()
            
        @self.event
        def on_draw():
            self.clear()
            self.view.draw() #Draws the apps to the screen
            if self.show_fps:
                self.fps.draw() #FPS Timer
                
        @self.event
        def on_key_press(symbol, modifiers):
            command = PygletKeyboardCommand(symbol, modifiers)
            if command.stop:
                stop = controller.quit()
                if stop:
                    pyglet.app.exit()
            if command.decision or command.selection:
                self.controller.override_bci_input(command)
                
                
    def start(self, control_manager_poll_for_next_command_fn):
        pyglet.clock.schedule(control_manager_poll_for_next_command_fn)
        pyglet.app.run()
        
        