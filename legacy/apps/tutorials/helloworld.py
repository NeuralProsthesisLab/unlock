from core import UnlockApplication
from random import randint

class HelloWorld(UnlockApplication):
    """
    Sample Unlock application for testing framework.
    Displays the words Hello World. Arrow keys move the words,
    and hitting the space bar re-centers them and changes the
    color of the text
    """

    name = "Hello World"
    icon = "robot.png"

    def __init__(self, screen):

        super(self.__class__, self).__init__(screen)
        self.text = screen.drawText('Hello World!', screen.width / 2,
                                    screen.height / 2)
        self.x_center = self.text.x
        self.y_center = self.text.y
        self.rect = screen.drawRect(0, 0, screen.width, screen.height)

    def update(self, dt, decision, selection):
        """Updates with every new decision or selection"""
        if decision is not None:
            if decision == 1:
                self.text.x = self.x_center
                self.text.y = self.y_center + 100
            elif decision == 2:
                self.text.x = self.x_center
                self.text.y = self.y_center - 100
            elif decision == 3:
                self.text.x = self.x_center - 100
                self.text.y = self.y_center
            elif decision == 4:
                self.text.x = self.x_center + 100
                self.text.y = self.y_center

        if selection:
            if self.text.y == self.y_center + 100:
                self.text.color = (255, 255, 255, 255)
                self.close()
            else:
                self.text.color = (randint(0,255), randint(0,255),
                                   randint(0,255), 255)
            self.text.x = self.x_center
            self.text.y = self.y_center