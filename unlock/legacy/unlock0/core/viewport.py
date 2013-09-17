import pyglet
from pyglet.window import key
from core import Controller

window = pyglet.window.Window(fullscreen=True, vsync=False)
controller = Controller([])
fps = pyglet.clock.ClockDisplay()

@window.event
def on_draw():
    """clears the window, and draws results from controller"""

    window.clear()
    controller.draw() #Draws the apps to the screen
    fps.draw() #FPS Timer

@window.event
def on_key_press(symbol, modifiers):
    """Handles Key pressing events."""

    if symbol == key.UP: #Up arrow key
        controller.debug_commands['decision'] = 1
    elif symbol == key.DOWN: #Down arrow key
        controller.debug_commands['decision'] = 2
    elif symbol == key.LEFT: #Left arrow key
        controller.debug_commands['decision'] = 3
    elif symbol == key.RIGHT: #Right arrow key
        controller.debug_commands['decision'] = 4
    elif symbol == key.SPACE: #Space bar
        controller.debug_commands['selection'] = 1
    elif symbol == key.ESCAPE: #Escape Key
        controller.quit()
        pyglet.app.exit()

def start():
    """ Starts the clock and starts the Unlock Interface"""
    pyglet.clock.schedule(controller.update)
    pyglet.app.run()