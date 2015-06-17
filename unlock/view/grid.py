from unlock.state import UnlockState, GridStateChange
from unlock.view.pyglet_sprite import PygletSprite
from unlock.view.pyglet_text import PygletTextLabel, PygletHTMLTextLabel
from unlock.view.view import UnlockView

from random import Random
import inspect
import pyglet
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
        fixed_state = UnlockState(state=True)
        name = "Unlock Dashboard"
        path=os.path.join(os.path.dirname(inspect.getabsfile(GridView)), 'unlock.png')
        try:
            abstract_image = pyglet.image.load(path)
            unlock_widget = PygletSprite(fixed_state, canvas, abstract_image, center_x, center_y, 0)
        except AttributeError:
            unlock_widget = PygletTextLabel(fixed_state, canvas, name,center_x, center_y, size=18)

        unlock_widget.render()
        self.icon_widgets.append(unlock_widget)

        for icon_path, icon_name in icons:
            x_offset, y_offset = model.ordering[index]
            icon_x = center_x + x_offset * icon_width
            icon_y = center_y + y_offset * icon_height
            try:
                abstract_image = pyglet.image.load(icon_path)
                icon_widget = PygletSprite(fixed_state, canvas, abstract_image, icon_x, icon_y, 0)
            except AttributeError:
                icon_widget = PygletTextLabel(fixed_state, canvas, icon_name, icon_x, icon_y, size=18)

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
                 tile_height=100, enable_gaze_control=False):
        super(HierarchyGridView, self).__init__()

        self.model = model
        self.canvas = canvas
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.xcenter = canvas.width / 2
        self.ycenter = canvas.height / 2
        self.xtiles = xtiles
        self.ytiles = ytiles
        self.xoffset = self.xcenter - (self.xtiles * tile_width) / 2
        self.yoffset = self.ycenter - (self.ytiles * tile_height) / 2
        self.grid_lines = self.drawGrid(self.xoffset, self.yoffset, xtiles, ytiles,
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

        if enable_gaze_control:
            cx, cy = canvas.center()
            self.gaze_cursor = PygletTextLabel(UnlockState(True), canvas, '\u271b', cx, cy)
        else:
            self.gaze_cursor = None
        
    def generate_target_coordinates(self):
        return self.rand.randint(self.xmin, self.xmax), self.rand.randint(self.ymin, self.ymax)
        
    def assign_target(self):
        self.xcoord, self.ycoord = self.generate_target_coordinates()        
        self.target = self.drawRect(self.xcenter - self.tile_width / 2 + self.xcoord*self.tile_width,
                                    self.ycenter - self.tile_height / 2 + self.ycoord*self.tile_height,
                                    self.tile_width - 1, self.tile_height - 1,
                                    self.canvas.batch, color=(0,255,128),
                                    fill=True)

    def mark_target(self):
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
            self.cursor.vertices[::2] = [i + int(state.step_value)*self.tile_width for i in self.cursor.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.cursor.vertices[1::2] = [i + int(state.step_value)*self.tile_height for i in self.cursor.vertices[1::2]]
        elif state.change == GridStateChange.Select:
            if state.step_value == (self.xcoord,self.ycoord):
                self.target.delete()
#                self.mark_target()
                self.assign_target()

        if state.gaze is not None and self.gaze_cursor is not None:
            gx = state.gaze[0]
            gy = self.canvas.height - state.gaze[1]
            xtile = int((gx - self.xoffset) / self.tile_width)
            ytile = int((gy - self.yoffset) / self.tile_height)
            if self.xoffset < gx < self.xoffset + self.tile_width * self.xtiles:
                self.gaze_cursor.label.x = int(self.xoffset + (xtile + 0.5) * self.tile_width)
            if self.yoffset < gy < self.yoffset + self.tile_height * self.ytiles:
                self.gaze_cursor.label.y = int(self.yoffset + (ytile + 0.5) * self.tile_height)
            if state.change == GridStateChange.Select:
                if (xtile - 2, ytile - 2) == (self.xcoord, self.ycoord):
                    self.target.delete()
                    self.assign_target()


class GridSpeakView(HierarchyGridView):
    def __init__(self, gridtext_2d_tuple, model, canvas, tile_width=100, tile_height=100, gender='Female'):
        ''' Requires a 2d tuple of lists of equal length, a gridmodel and a canvas '''
        #length = len(gridtext_2d_tuple[0])
        #for row in gridtext_2d_tuple:
        #    assert len(row) == length
                
        super(GridSpeakView, self).__init__(model, canvas)#,len(gridtext_2d_tuple[0]), len(gridtext_2d_tuple))
        # XXX - this needs to get pushed into configuration data
        self.target.delete()
        self.target = None
        self.cursor.delete()
        self.cursor = self.drawRect(self.xcenter - (tile_width-10) / 2,
                                    self.ycenter - (tile_height-10) / 2,
                                    tile_width - 10, tile_height - 10,
                                    canvas.batch, color=(255,0,0),
                                    fill=False)
        path = os.path.dirname(inspect.getfile(GridSpeakView))
        self.alone = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender, 'alone.wav')))
        self.bored = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender, 'bored.wav')))
        self.down = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender, 'down.wav')))
        self.explain = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'explain.wav')))
        self.get = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'get.wav')))
        self.goodbye = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'goodbye.wav')))
        self.hello = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'hello.wav')))
        self.help = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'help.wav')))
        self.howareyou = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'howareyou.wav')))
        self.hungah = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender , 'hungry.wav')))
        self.left = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'left.wav')))
        self.move = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'move.wav')))
        self.no = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'no.wav')))
        self.nose = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'nose.wav')))
        self.pain = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'pain.wav')))
        self.repeat = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'repeat.wav')))        
        self.right = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'right.wav')))
        self.sorry = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'sorry.wav')))
        self.thanks = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'thanks.wav')))                        
        self.thirsty = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'thirsty.wav')))
        self.up = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'up.wav')))                        
        self.when = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'when.wav')))                        
        self.where = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'where.wav')))
        self.who = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'who.wav')))                        
        self.yes = pyglet.media.StaticSource(pyglet.media.load(os.path.join(path, 'resource', 'sounds', gender,  'yes.wav')))                        
        self.words = {
            (-2, -2): ('alone', self.alone), (-2, -1): ('bored',self.bored), (-2,0): ('down', self.down), (-2,1):('explain', self.explain),(-2,2):('get', self.get),
            (-1,-2):('goodbye', self.goodbye), (-1,-1):('hello', self.hello), (-1,0):('help', self.help), (-1,1):('how R U', self.howareyou), (-1,2):('hungry', self.hungah),
            (0,-2):('left', self.left), (0,-1):('move', self.move), (0,0):('no',self.no), (0,1):('nose', self.nose), (0,2):('pain',self.pain),
            (1,-2):('repeat', self.repeat), (1,-1):('right', self.right), (1,0):('sorry', self.sorry), (1,1):('thanks', self.thanks), (1,2):('thirsty', self.thirsty),
            (2,-2): ('up', self.up), (2,-1):('when', self.when), (2,0):('where', self.where), (2,1):('who', self.who), (2,2):('yes', self.yes)
        }
        self.labels = []
        self.draw_words(gridtext_2d_tuple, model, canvas, self.xoffset, self.yoffset)       
    
    def draw_words(self, gridtext_2d_tuple, model, canvas, x_offset, y_offset):#, rows, columns, tile_width,
        for k,v in self.words.items():
            xoffset = self.xcenter+self.tile_width*(k[0])
            yoffset = self.ycenter+self.tile_height*(k[1])
            label = PygletTextLabel(model, canvas, v[0], xoffset, yoffset, anchor_x='center', anchor_y='center', width=self.tile_width-1, size=18)
            label.label.multiline = True
            self.labels.append(label)
                
    def render(self):
        state = self.model.get_state()
        if not state:
            return
            
        if state.change == GridStateChange.XChange:
            self.cursor.vertices[::2] = [i + int(state.step_value)*self.tile_width for i in self.cursor.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.cursor.vertices[1::2] = [i + int(state.step_value)*self.tile_height for i in self.cursor.vertices[1::2]]
        elif state.change == GridStateChange.Select and state.gaze is None:
            self.words[state.step_value][1].play()

        if state.gaze is not None and self.gaze_cursor is not None:
            gx = state.gaze[0]
            gy = self.canvas.height - state.gaze[1]
            xtile = int((gx - self.xoffset) / self.tile_width)
            ytile = int((gy - self.yoffset) / self.tile_height)
            if self.xoffset < gx < self.xoffset + self.tile_width * self.xtiles:
                self.gaze_cursor.label.x = int(self.xoffset + (xtile + 0.5) * self.tile_width)
            if self.yoffset < gy < self.yoffset + self.tile_height * self.ytiles:
                self.gaze_cursor.label.y = int(self.yoffset + (ytile + 0.5) * self.tile_height)
            if state.change == GridStateChange.Select:
                self.words[(xtile - 2, ytile - 2)][1].play()



class RobotGridView(HierarchyGridView):
    def __init__(self, model, canvas, xtiles=5, ytiles=5, tile_width=100,
                 tile_height=100):
        super(RobotGridView, self).__init__(model, canvas, xtiles, ytiles,
                                            tile_width, tile_height)
        self.target.delete()
        self.target = None
        self.cursor.delete()
        self.cursor = self.drawRect(self.xcenter - (tile_width-10) / 2,
                                    self.ycenter - (tile_height-10) / 2,
                                    tile_width - 10, tile_height - 10,
                                    canvas.batch, color=(255,0,0),
                                    fill=False)
        self.obj1 = self.drawRect((self.xcenter + tile_height) - (tile_width-50) / 2,
                                  self.ycenter - (tile_height-50) / 2,
                                  tile_width - 50, tile_height - 50,
                                  canvas.batch, color=(0,255,0),
                                  fill=True)
        self.obj2 = self.drawRect((self.xcenter - tile_height) - (tile_width-50) / 2,
                                  self.ycenter - (tile_height-50) / 2,
                                  tile_width - 50, tile_height - 50,
                                  canvas.batch, color=(255,0,255),
                                  fill=True)
        self.obj3 = self.drawRect(self.xcenter - (tile_width-50) / 2,
                                  (self.ycenter + tile_height) - (tile_height-50) / 2,
                                  tile_width - 50, tile_height - 50,
                                  canvas.batch, color=(255,69,0),
                                  fill=True)
        self.obj4 = self.drawRect(self.xcenter - (tile_width-50) / 2,
                                  (self.ycenter - tile_height) - (tile_height-50) / 2,
                                  tile_width - 50, tile_height - 50,
                                  canvas.batch, color=(139,0,0),
                                  fill=True)

    def render(self):
        state = self.model.get_state()
        if not state:
            return

        if state.change == GridStateChange.XChange:
            self.cursor.vertices[::2] = [i + int(state.step_value)*self.tile_width for i in self.cursor.vertices[::2]]
        elif state.change == GridStateChange.YChange:
            self.cursor.vertices[1::2] = [i + int(state.step_value)*self.tile_height for i in self.cursor.vertices[1::2]]

        if state.gaze is not None and self.gaze_cursor is not None:
            gx = state.gaze[0]
            gy = self.canvas.height - state.gaze[1]
            xtile = int((gx - self.xoffset) / self.tile_width)
            ytile = int((gy - self.yoffset) / self.tile_height)
            if self.xoffset < gx < self.xoffset + self.tile_width * self.xtiles:
                self.gaze_cursor.label.x = int(self.xoffset + (xtile + 0.5) * self.tile_width)
            if self.yoffset < gy < self.yoffset + self.tile_height * self.ytiles:
                self.gaze_cursor.label.y = int(self.yoffset + (ytile + 0.5) * self.tile_height)
