from unlock import PygletTextLabel, BellRingTextLabelDecorator
from unlock import PygletWindow, Canvas, UnlockController, AlternatingBinaryStateModel

import unittest
import pyglet
import multiprocessing as mp


class PygletTextTests(unittest.TestCase):       
    def testPygletText(self):
        window = PygletWindow(fullscreen=False, show_fps=True)
        canvas = Canvas.create(window.width, window.height)
        model = AlternatingBinaryStateModel()
        pos = PositionMixin()
        text_label = PygletTextLabel(model, canvas, 'the text', canvas.width / 2.0, canvas.height / 2.0)
        bell_ring_text_label_decorator = BellRingTextLabelDecorator(text_label)        
        controller = UnlockController(window, [bell_ring_text_label_decorator], canvas)
        controller.make_active()
        window.start()        
        window.close()
        
        
def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()

