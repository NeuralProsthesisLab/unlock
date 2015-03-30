__author__ = 'Graham Voysey'
from unlock.view.view import UnlockView
import pyautogui
import time

class FEMGView(UnlockView):
    def __init__(self, state, canvas):
        super(FEMGView, self).__init__()
        self.state = state
        self.canvas = canvas

    def render(self):
        screenWidth, screenHeight = pyautogui.size()
        #currentMouseX, currentMouseY = pyautogui.position()
        #pyautogui.moveTo(100, 150)
        #pyautogui.moveTo(500, 500, duration=2, tween=pyautogui.tweens.easeInOutQuad)  # use tweening/easing function to move mouse over 2 seconds.
        #pyautogui.press('esc')
        pyautogui.keyDown('left',2)


       # m = PyMouse()
       #  x,y = m.screen_size()
       #  mx,my=m.position()
       #  m.move(0,0)
       #  m.move(x,y)
