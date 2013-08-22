
from unlock.util import DelegatorMixin


class UnlockModel(object):
    def __init__(self, state=None):
        super(UnlockModel, self).__init__()
        self.state = state
        
    def start(self):
        pass
        
    def stop(self):
        pass
        
    def is_stopped(self):
        pass
        
    def get_state(self):
        return self.state
        
        
class AlternatingBinaryStateModel(UnlockModel):
    def __init__(self, hold_duration=300):
        self.hold_duration = hold_duration
        self.state = True
        self.count = 0
        
    def get_state(self):
        ret = self.state
        self.count += 1
        if self.count % self.hold_duration == 0:
            self.state = not self.state
        return ret
            
            
class PositionMixin(object):
    def __init__(self, x_offset, y_offset, anchor_x='center', anchor_y='center'):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_anchor = anchor_x
        self.y_anchor = anchor_y
            
            
class GraphicModel(DelegatorMixin):
    def __init__(self, state_model, canvas, position):
        super(GraphicModel, self).__init__()
        self.add_delegate(state_model)
        self.add_delegate(canvas)
        self.add_delegate(position)
        self.state_model = state_model
        self.canvas = canvas
        self.position = position
            
            
class TextGraphic(GraphicModel):
    def __init__(self, state_model, canvas, position, text, font='Helvetica', font_size=48,
                 font_color=(255,255,255,255), group=None):
        super(TextGraphic, self).__init__(state_model, canvas, position)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        if len(font_color) == 3:
            self.font_color = font_color + (255,)
        self.group = group
            
           
class ImageGraphic(GraphicModel):
    def __init__(self, state_model, canvas, position, filename):
        super(TextGraphic, self).__init__(state_model, canvas, position)
        self.filename = filename
        
        