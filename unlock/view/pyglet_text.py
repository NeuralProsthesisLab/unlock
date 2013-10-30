from unlock.view.view import UnlockView

import pyglet
import inspect
import logging
import os

class PygletLabel(UnlockView):
    def __init__(self, model, canvas, text, x, y, color=(255,255,255,255)):
        super(PygletLabel, self).__init__()
        self.model = model
        self.canvas = canvas
        self.text = text
        self.x = x
        self.y = y
        self.state = True
        self.label = None
        if len(color) == 3:
            color = color + (255,)
        self.color = color        
        self.logger = logging.getLogger(__name__)
        
    def render(self):
        self.last_state = self.state
        self.state = self.model.get_state()
        
        if self.state and self.label is not None:
            self.label.text = self.text
        elif self.label is not None:
            self.label.text = ''
            
            
class PygletTextLabel(PygletLabel):
    def __init__(self, model, canvas, text, x, y, width=None, height=None, anchor_x='center', anchor_y='center', font='Helvetica', size=48,
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
        super(PygletTextLabel, self).__init__(model, canvas, text, x, y, color)
        self.font = font
        self.size = size
        if width != None and height != None:
            self.label = pyglet.text.Label(self.text, font_name=self.font, font_size=self.size,
                                        x=self.canvas.x+self.x, y=self.canvas.y+self.y,
                                        anchor_x=anchor_x, anchor_y=anchor_y, color=self.color, width=width, height=height,
                                        group=group,batch=self.canvas.batch)
        else:
            self.label = pyglet.text.Label(self.text, font_name=self.font, font_size=self.size,
                            x=self.canvas.x+self.x, y=self.canvas.y+self.y,
                            anchor_x=anchor_x, anchor_y=anchor_y, color=self.color, width=width, height=height,
                            group=group,batch=self.canvas.batch)
            
        self.label.text = text
        self.logger = logging.getLogger(__name__)
        
        
class PygletHTMLTextLabel(PygletLabel):
    def __init__(self, model, canvas, text, x, y, anchor_x='center', anchor_y='center', font='Helvetica', size=18,
                 color=(255,255,255,255), group=None):
        super(PygletHTMLTextLabel, self).__init__(model, canvas, text, x, y, color)
        self.label = pyglet.text.HTMLLabel(text=text,
                                    x=self.canvas.x+self.x, y=self.canvas.y+self.y,
                                    anchor_x=anchor_x, anchor_y=anchor_y, width=100, height=100,
                                    group=group,batch=self.canvas.batch)
        self.label.color = self.color
        self.logger = logging.getLogger(__name__)
        
class DynamicPositionPygletTextLabel(PygletTextLabel):
    def __init__(self,  model, canvas, text, x, y, anchor_x='center', anchor_y='center', font='Helvetica', size=48,
                 color=(255,255,255,255), group=None):
        super(DynamicPositionPygletTextLabel, self).__init__(model, canvas, text, x, y, anchor_x, anchor_y, font, size, color, group)
    def render(self):
        self.last_state = self.state
        self.x, self.y, self.state = self.model.get_state()
        #print "x = ", self.x, " self.y = ", self.y, " state = ", self.state
        self.logger.debug("PygletTextLabel text = ", self.label.text, " last state, state = ", self.last_state, self.state)
        
        if self.state:
            self.label.text = self.text
            self.label.x = self.x
            self.label.y = self.y            
        else:
            self.label.text = ''
        
            
class BellRingTextLabelDecorator(UnlockView):
    def __init__(self, text_label):
        super(BellRingTextLabelDecorator, self).__init__()
        self.text_label = text_label
        self.model = self.text_label.model
        self.sound = pyglet.media.StaticSource(pyglet.media.load(os.path.join(os.path.dirname(inspect.getfile(BellRingTextLabelDecorator)), 'bell-ring-01.mp3')))
        self.state = True
        self.logger = logging.getLogger(__name__)        
        
    def render(self):   
        self.last_state = self.state
        self.state = self.model.get_state()
        self.logger.debug("BellRingTextLabelDecorator text = ", self.text_label.label.text, " last state, state = ", self.last_state, self.state)
            
        if self.state:
            if self.last_state != self.state:
                pass
                self.sound.play()
                
            self.text_label.label.text = self.text_label.text
        else:
            self.text_label.label.text = ''
            
         