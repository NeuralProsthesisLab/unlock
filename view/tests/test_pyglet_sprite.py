from .. import SpritePositionComputer, PygletSprite, FlickeringPygletSprite, PygletWindow, ScreenDescriptor, App

import unittest
import pyglet
import multiprocessing as mp


class PygletSpriteTests(unittest.TestCase):       
    def testMSequencePygletSprite(self):
        #window = PygletWindow(fullscreen=True, show_fps=True)        
        #screen = ScreenDescriptor.create(window.width, window.height)
        #app = App()
        #window.set_app(app)
        #fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(BasicModel(), screen, SpritePositionComputer.North)
        #window.add_view(fs)
        #window.switch_to()        
        #window.start()
        #window.clear()
        #window.close()
        #
        
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
        window.switch_to()
        window.start()        
        window.close()

def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()
    #p = PygletSpriteTests()
    #p.testMSequencePygletSprite()
    