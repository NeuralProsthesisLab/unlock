from .. import SpritePositionComputer, PygletSprite, FlickeringPygletSprite, PygletWindow, ScreenDescriptor, App

import unittest
import pyglet


class BasicModel:
    def __init__(self):
        self.state_value = False
    def state(self):
        self.state_value = not self.state_value
        return self.state_value

class PygletSpriteTests(unittest.TestCase):
    #def testFlickeringPygletSprite(self):
    #    window = PygletWindow(fullscreen=True, show_fps=True)        
    #    screen = ScreenDescriptor.create(window.width, window.height)
    #    app = App()
    #    window.set_app(app)
    #    fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, PygletSprite.configure_north)
    #    fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, PygletSprite.configure_east, 90)
    #    fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, PygletSprite.configure_south)
    #    fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, PygletSprite.configure_west, 90)        
    #    window.add_view(fs)
    #    window.add_view(fs1)
    #    window.add_view(fs2)
    #    window.add_view(fs3)        
    #    window.start()
    def testMSequencePygletSprite(self):
        window = PygletWindow(fullscreen=True, show_fps=True)        
        screen = ScreenDescriptor.create(window.width, window.height)
        app = App()
        window.set_app(app)
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, SpritePositionComputer.North, width=200, height=200,
            xfreq=4, yfreq=4)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, SpritePositionComputer.East, 90, width=200, height=200,
            xfreq=4, yfreq=4)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, SpritePositionComputer.South, width=200, height=200,
            xfreq=4, yfreq=4)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, SpritePositionComputer.West, 90, width=200, height=200,
            xfreq=4, yfreq=4)        
        window.add_view(fs)
        window.add_view(fs1)
        window.add_view(fs2)
        window.add_view(fs3)        
        window.start()        
        
        
def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()
    