from .. import PygletSprite, FlickeringPygletSprite, PygletWindow, ScreenDescriptor, App

import unittest
import pyglet


class BasicModel:
    def __init__(self):
        self.state_value = False
    def state(self):
        self.state_value = not self.state_value
        return self.state_value

class PygletSpriteTests(unittest.TestCase):
    def testFlickeringPygletSprite(self):
        window = PygletWindow(fullscreen=False, show_fps=True)        
        model = BasicModel()
        screen = ScreenDescriptor.create(window.width, window.height)
        app = App()
        window.set_app(app)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(model, screen, PygletSprite.configure_center)
        window.add_view(fs)
        window.start()

        
def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()
    