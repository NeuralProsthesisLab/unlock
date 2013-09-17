from core import UnlockApplication
from random import randint

class Rectangle1(UnlockApplication):
    name = "rectangle_1"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()


        half_w  = w/2
        half_h  = h/2

#        red   = (255,0,0)
        green = (0,255,0)

#        self.rect1  = screen.drawRect(0,0, w, h, color=red)
        self.rect2  = screen.drawRect(0,0, half_w, half_h, color=green)


    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        pass

class Rectangle2(UnlockApplication):
    name = "rectangle_2"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()

        buffer = {'r':0.05, 'g':0.25}

        originR = [w*buffer['r'],h*buffer['r']]
        originG = [w*buffer['g'],h*buffer['g']]

        sizeR   = [w*(1-2*buffer['r']),h*(1-2*buffer['r'])]
        sizeG   = [w*(1-2*buffer['g']),h*(1-2*buffer['g'])]

        red   = (255,0,0)
        green = (0,255,0)

#        self.rect1  = screen.drawRect(originR[0],originR[1], sizeR[0], sizeR[1], color=red)
        self.rect2  = screen.drawRect(originG[0],originG[1], sizeG[0], sizeG[1], color=green)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        pass

class Rectangle3(UnlockApplication):
    name = "rectangle_3"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        w       = screen.get_width()
        h       = screen.get_height()

        buffer = {'r':0.05, 'g':0.25}
        originG = [w*buffer['g'],h*buffer['g']]
        sizeG   = [w*(1-2*buffer['g']),h*(1-2*buffer['g'])]

        self.x_pix = 10
        self.y_pix = 10

        green = (0,255,0)

        self.rect1  = screen.drawRect(originG[0],originG[1], sizeG[0], sizeG[1], color=green)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""

        if decision:
            if decision == 1:
                self.moveBox(self.rect1,0,1)
            elif decision == 2:
                self.moveBox(self.rect1,0,-1)
            elif decision == 3:
                self.moveBox(self.rect1,-1,0)
            elif decision == 4:
                self.moveBox(self.rect1,1,0)


    def moveBox(self, box, x_step, y_step):
        """Moves box by n x_step or y_step. x_step and y_step are
            defined by the height of the grid elements"""
        if x_step:
            box.vertices[::2] = [i + int(x_step)*self.x_pix for i in box.vertices[::2]]
        if y_step:
            box.vertices[1::2] = [i + int(y_step)*self.y_pix for i in box.vertices[1::2]]

