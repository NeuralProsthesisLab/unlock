import pyglet
from pyglet.window import key
from core import Controller

window = pyglet.window.Window(fullscreen=True, vsync=False)
controller = Controller([])
fps = pyglet.clock.ClockDisplay()
show_fps = False

@window.event
def on_draw():
    """clears the window, and draws results from controller"""

    window.clear()
    controller.draw() #Draws the apps to the screen
    if show_fps:
        fps.draw() #FPS Timer

@window.event
def on_key_press(symbol, modifiers):
    """Handles Key pressing events."""
    labels = [ord(c) for c in 'abcdefghijklmnopqrstuvwxyz_12345']
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
        stop = controller.quit()
        if stop:
            pyglet.app.exit()
    elif symbol in labels:
        controller.debug_commands['decision'] = labels.index(symbol) + 1

def start():
    """ Starts the clock and starts the Unlock Interface"""
    pyglet.clock.schedule(controller.update)
    pyglet.app.run()