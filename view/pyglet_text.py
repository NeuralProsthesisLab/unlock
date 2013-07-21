from view import UnlockView

import pyglet
import inspect
import os

class PygletTextLabel(UnlockView):
    def __init__(self, model, screen, text, x, y, anchor_x='center', anchor_y='center', font='Helvetica', size=48,
                 color=(255,255,255,255), group=None):
        """
        Draws text at a specific point on the screen

        :param text: Text to display
        :param x: x-coordinate of center of text(Pixels from left)
        :param y: y-coordinate of center of text(Pixels from bottom)
        :param font: Font of text
        :param size: Size of text
        :param color: Color of text. Tuple of length four.
        """
        self.model = model
        self.screen = screen
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.size = size

        if len(color) == 3:
            color = color + (255,)
        self.color = color
        self.label = pyglet.text.Label(self.text, font_name=self.font, font_size=self.size,
                                    x=self.screen.x+self.x, y=self.screen.y+self.y,
                                    anchor_x=anchor_x, anchor_y=anchor_y, color=self.color,
                                    group=group,batch=self.screen.batch)
        self.label.text = text
        
    def render(self):
        if self.model.get_state():
            self.label.text = self.text
        else:
            self.label.text = ''
            
        self.screen.batch.draw()
        

class BellRingTextLabelDecorator(UnlockView):
    def __init__(self, text_label):
        self.text_label = text_label
        self.model = self.text_label.model
        self.sound = pyglet.media.StaticSource(pyglet.media.load(os.path.join(os.path.dirname(inspect.getfile(BellRingTextLabelDecorator)), 'bell-ring-01.mp3')))
        self.state = True
        
    def render(self):
        self.last_state = self.state
        self.state = self.model.get_state()
        if self.last_state != self.state:
            self.sound.play()
            
        if self.state:
            self.text_label.label.text = self.text_label.text
        else:
            self.text_label.label.text = ''
            
        self.text_label.screen.batch.draw()
   



#class Image(object):
#    def __init__(self, window, filename, anchor_x, anchor_y, position_x, position_y):
#        self.window = window
#        self.filename = filename
#        self.anchor_x = anchor_x
#        self.anchor_y = anchor_y
#        self.position_x = position_x
#        self.position_y = position_y
#        self.prepare_draw()
#    def prepare_draw(self):          
#        self.window.clear()
#        img = pyglet.image.load(self.filename).get_texture(rectangle=True)
#        img.anchor_x = self.anchor_x
#        img.anchor_y = self.anchor_y
#        self.window.set_visible()
#        self.img = img
#    def draw(self):
#        self.img.blit(self.position_x, self.position_y, 0)
#        
#     