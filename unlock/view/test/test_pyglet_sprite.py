from unlock import SpritePositionComputer, PygletSprite, FlickeringPygletSprite, PygletWindow, Canvas, UnlockController, AlternatingBinaryStateModel

import unittest
import pyglet
import multiprocessing as mp


class PygletSpriteTests(unittest.TestCase):       
    def testMSequencePygletSprite(self):
        #window = PygletController(fullscreen=True, show_fps=True)        
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
        
        window = PygletWindow(fullscreen=False, show_fps=True)
        canvas = Canvas.create(window.width, window.height)

        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(AlternatingBinaryStateModel(hold_duration=5), canvas, SpritePositionComputer.North, width=200, height=200,
            xfreq=4, yfreq=4)
            
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(AlternatingBinaryStateModel(hold_duration=5), canvas, SpritePositionComputer.East, 90, width=200, height=200,
            xfreq=4, yfreq=4)
            
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(AlternatingBinaryStateModel(hold_duration=5), canvas, SpritePositionComputer.South, width=200, height=200,
            xfreq=4, yfreq=4)
            
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(AlternatingBinaryStateModel(hold_duration=5), canvas, SpritePositionComputer.West, 90, width=200, height=200,
            xfreq=4, yfreq=4)
        controller = UnlockController(window, [fs, fs1, fs2, fs3], canvas)
        controller.make_active()
        window.switch_to()
        window.start()        
        window.close()

def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()
    