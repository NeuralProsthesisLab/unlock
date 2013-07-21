from unlock import PygletTextLabel, BellRingTextLabelDecorator
from unlock import PygletController, ScreenDescriptor, App

import unittest
import pyglet
import multiprocessing as mp

class Model:
    def __init__(self):
        self.state = True
        self.count = 0
    def get_state(self):
        ret = self.state
        self.count += 1
        if self.count % 311 == 0:
            #raise
            self.state = not self.state
        return ret

class PygletTextTests(unittest.TestCase):       
    def testPygletText(self):
        window = PygletController(fullscreen=False, show_fps=True)
        screen = ScreenDescriptor.create(window.width, window.height)
        app = App()
        model = Model()
        window.set_app(app)
        text_label = PygletTextLabel(model, screen, 'the text', screen.width / 2.0, screen.height / 2.0)
        bell_ring_text_label_decorator = BellRingTextLabelDecorator(text_label)
        window.add_view(bell_ring_text_label_decorator)
        window.switch_to()
        window.start()        
        window.close()

def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()
    #p = PygletSpriteTests()
    #p.testMSequencePygletSprite()
    