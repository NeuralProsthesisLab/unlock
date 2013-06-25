import pyglet
import controller
from util import observer

class PygletWindow(pyglet.window.Window):
    def __init__(self, controller=controller.Controller([]), fullscreen=False, vsync=False, show_fps=False):
        super(PygletWindow, self).__init__(**{'fullscreen':fullscreen, 'vsync':vsync})
        self.controller = controller
        self.show_fps = show_fps
        self.fps = pyglet.clock.ClockDisplay()
        @self.event
        def on_draw():
            """clears the window, and draws results from controller"""
    
            self.clear()
            self.controller.draw() #Draws the apps to the screen
            if self.show_fps:
                self.fps.draw() #FPS Timer
                
        @self.event
        def on_key_press(symbol, modifiers):
            from pyglet.window import key
            """Handles Key pressing events."""
            labels = [ord(c) for c in 'abcdefghijklmnopqrstuvwxyz_12345']
            if symbol == key.UP: #Up arrow key
                self.controller.debug_commands['decision'] = 1
            elif symbol == key.DOWN: #Down arrow key
                self.controller.debug_commands['decision'] = 2
            elif symbol == key.LEFT: #Left arrow key
                self.controller.debug_commands['decision'] = 3
            elif symbol == key.RIGHT: #Right arrow key
                self.controller.debug_commands['decision'] = 4
            elif symbol == key.SPACE: #Space bar
                self.controller.debug_commands['selection'] = 1
            elif symbol == key.ESCAPE: #Escape Key
                stop = controller.quit()
                if stop:
                    pyglet.app.exit()
            elif symbol in labels:
                self.controller.debug_commands['decision'] = labels.index(symbol) + 1
    
    def start(self):
        """ Starts the clock and starts the Unlock Interface"""
        pyglet.clock.schedule(self.controller.update)
        pyglet.app.run()
        
        