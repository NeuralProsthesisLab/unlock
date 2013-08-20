from unlock import Canvas, UnlockModel, TextGraphic, PositionMixin, BellRingTextLabelDecorator, PygletWindow, PygletTextLabel, UnlockController, AlternatingBinaryStateModel, DelegatorMixin

import unittest
import pyglet
import multiprocessing as mp


class ModelTests(unittest.TestCase):       
    def testTextGraphic(self):
        window = PygletWindow(fullscreen=False, show_fps=True)
        state_model = AlternatingBinaryStateModel(hold_duration=125)
        canvas = Canvas.create(window.width, window.height)
        pos = PositionMixin(canvas.xcenter(), canvas.ycenter())
        text_graphic_model = TextGraphic(state_model, canvas, pos, "+")
        #self.text_graphic_model.x_offset
            
        text_label = PygletTextLabel(text_graphic_model)
        bell_ring_text_label_decorator = BellRingTextLabelDecorator(text_label)        
        controller = UnlockController(window, [bell_ring_text_label_decorator], canvas)
        controller.activate()
        window.start()        
        window.close()
        
    #def testDelegatorMixin(self):
    #    d = DelegatorMixin()
    #    a = AttrTest()
    #    a1 = AttrTest()
    #    a1.a = 111
    #    a1.b = 111
    #    a1.c = 111
    #    
    #    a1.c = "A1F"
    #    d.add_delegate(a)
    #    d.add_delegate(a1)
    #    d.g = "DG"
    #    d.c = 222
    #    d.d()
    #    d.e(1,3)
    #    
    #    self.assertEquals(0, d.a)
    #    self.assertEquals(1, d.b)
    #    self.assertEquals(222, d.c)
    #    self.assertEquals(True, d.d_value)
    #    self.assertEquals(1, d.e_value)
    #    self.assertEquals(3, d.e1_value)
    #    self.assertEquals("DG", d.g)
    #        
            
def getSuite():
    return unittest.makeSuite(PygletSpriteTests,'test')

if __name__ == "__main__":
    unittest.main()

