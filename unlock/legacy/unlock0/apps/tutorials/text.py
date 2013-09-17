from core import UnlockApplication
from random import randint

class Text1(UnlockApplication):
    name = "text_1"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()

        half_w  = w/2
        half_h  = h/2

        blue    = (0,0,255,255)

        text = 'Hello World'

        self.text1 = screen.drawText(text,half_w,half_h, color=blue)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        pass

class Text2(UnlockApplication):
    name = "text_2"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()

        half_w  = w/2
        half_h  = h/2

        blue    = (0,0,255,255)

        text = 'Hello World'

        self.text1 = screen.drawText(text,half_w,half_h, color=blue)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        if selection:
            self.text1.color = (randint(0,255), randint(0,255),
                               randint(0,255), 255)