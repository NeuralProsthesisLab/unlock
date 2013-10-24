from unlock.model import UnlockModel
from unlock.model import GridStateChange
from .pyglet_sprite import PygletSprite
from .pyglet_text import PygletTextLabel
from .view import UnlockView

from random import Random
import inspect
import time
import os


class GridView(UnlockView):
    def __init__(self, model, canvas, icons, center_x, center_y, rect_xoffset=64, rect_yoffset=64,
                 icon_width=128, icon_height=128):
        super(GridView, self).__init__()

        self.model = model
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.controller_count = 0
        self.cursor = (0,0)
        self.icon_widgets = []
        self.vertex_list = self.drawRect(center_x-rect_xoffset, center_y-rect_yoffset, icon_width, icon_height, canvas.batch)
        index = 0
        fixed_state_model = UnlockModel(state=True)
        name = "Unlock Dashboard"
        path=os.path.join(os.path.dirname(inspect.getabsfile(GridView)), 'unlock.png')
            
        try:
            unlock_widget = PygletSprite.create_image_sprite(fixed_state_model, canvas, path, center_x, center_y)
        except AttributeError:
            unlock_widget = PygletTextLabel(fixed_state_model, canvas, name,center_x, center_y, size=18)
            
        unlock_widget.render()
        self.icon_widgets.append(unlock_widget)
        
        for icon_path, icon_name in icons:
            x_offset, y_offset = model.ordering[index]
            icon_x = center_x + x_offset * icon_width
            icon_y = center_y + y_offset * icon_height
            try:
                icon_widget = PygletSprite.create_image_sprite(fixed_state_model, canvas, icon_path, icon_x, icon_y)
            except AttributeError:
                icon_widget = PygletTextLabel(fixed_state_model, canvas, icon_name, icon_x, icon_y, size=18)
                
            icon_widget.render()
            self.icon_widgets.append(icon_widget)
            index += 1
            
    def render(self):
        state = self.model.get_state()
        if not state:
            return
            
        if state.change == GridStateChange.XChange:
            self.vertex_list.vertices[::2] = [i + int(state.step_value)*self.icon_width for i in self.vertex_list.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.vertex_list.vertices[1::2] = [i + int(state.step_value)*self.icon_height for i in self.vertex_list.vertices[1::2]]
            
        for icon_widget in self.icon_widgets:
            icon_widget.render()


class HierarchyGridView(UnlockView):
    def __init__(self, model, canvas, xtiles=5, ytiles=5, tile_width=100,
                 tile_height=100):
        super(HierarchyGridView, self).__init__()

        self.model = model
        self.canvas = canvas
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.xcenter = canvas.width / 2
        self.ycenter = canvas.height / 2
        xoffset = self.xcenter - (xtiles * tile_width) / 2
        yoffset = self.ycenter - (ytiles * tile_height) / 2
        self.grid_lines = self.drawGrid(xoffset, yoffset, xtiles, ytiles,
                                        tile_width, tile_height, canvas.batch)
        
        assert xtiles % 2 != 0 and ytiles % 2 != 0
        self.xmax = int(xtiles / 2)
        self.xmin = int(xtiles / 2) * -1
        self.ymax = int(ytiles / 2)
        self.ymin = int(ytiles / 2) * -1
        self.rand = Random()
        self.rand.seed(time.time())
        
        self.assign_target()
        self.cursor = self.drawRect(self.xcenter - tile_width / 2,
                                    self.ycenter - tile_height / 2,
                                    tile_width - 1, tile_height - 1,
                                    canvas.batch, color=(0,128,255),
                                    fill=True)
        
    def generate_target_coordinates(self):
        return self.rand.randint(self.xmin, self.xmax), self.rand.randint(self.ymin, self.ymax)
        
    def assign_target(self):
        self.xcoord, self.ycoord = self.generate_target_coordinates()        
        self.target = self.drawRect(self.xcenter - self.tile_width / 2 + self.xcoord*self.tile_width,
                                    self.ycenter - self.tile_height / 2 + self.ycoord*self.tile_height,
                                    self.tile_width - 1, self.tile_height - 1,
                                    self.canvas.batch, color=(0,255,128),
                                    fill=True)
    def mark_target(self, ):
        self.target = self.drawRect(self.xcenter - self.tile_width / 2 + self.xcoord*self.tile_width,
                                    self.ycenter - self.tile_height / 2 + self.ycoord*self.tile_height,
                                    self.tile_width - 1, self.tile_height - 1,
                                    self.canvas.batch, color=(0,128,255),
                                    fill=False)
    
    def render(self):
        state = self.model.get_state()
        if not state:
            return
            
        if state.change == GridStateChange.XChange:
            self.cursor.vertices[::2] = [i + int(state.step_value)*self
            .tile_width for i in self.cursor.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.cursor.vertices[1::2] = [i + int(state.step_value)*self
            .tile_height for i in self.cursor.vertices[1::2]]
        elif state.change == GridStateChange.Select:
            if state.step_value == (self.xcoord,self.ycoord):
                self.target.delete()
#                self.mark_target()
                self.assign_target()
                
