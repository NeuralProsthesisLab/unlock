from core import UnlockApplication

class Line1(UnlockApplication):
    name = "line_1"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()

        half_w  = w/2
        half_h  = h/2

        red = (255,0,0)
        self.line1  = screen.drawLine(0, half_h, w, half_h)#, color=red)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        if selection is not None:
            self.close()