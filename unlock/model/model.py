# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from unlock.util import DelegatorMixin


class UnlockModel(object):
    def __init__(self, state=None):
        super(UnlockModel, self).__init__()
        self.state = state
        self.running = False
        
    def start(self):
        self.running = True
        
    def stop(self):
        self.running = False
        
    def is_stopped(self):
        return self.running
        
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
        
        