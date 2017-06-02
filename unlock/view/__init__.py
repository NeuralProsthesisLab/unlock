import array
import copy

import pyglet

from unlock.view.pyglet_sprite import *
from unlock.view.pyglet_text import *
from unlock.view.view import *
from unlock.view.grid import *
from unlock.view.fastpad_view import *
from unlock.view.scope_view import *
from unlock.view.robot_view import *


class UnlockViewFactory(object):

    def create_image_pyglet_sprit(self, model, canvas, filename, x=0, y=0, rotation=0):
        abstract_image = pyglet.image.load(filename)
        return PygletSprite(model, canvas, abstract_image, int(x), int(y), rotation)

    def create_checkerboard_sprite(self, model, canvas, cb_properties,
                                   position=SpritePositionComputer.Center,
                                   x_offset=0, y_offset=0, rotation=0):
        texture = self.create_checkerboard_texture(cb_properties)
        spc = SpritePositionComputer(canvas, texture.width, texture.height,
                                     rotation)
        spc.compute(position)

        sprite = PygletSprite(model, canvas, texture, spc.x + x_offset,
                              spc.y + y_offset, rotation)
        return sprite

    def create_image_sprite(self, model, canvas, filename, scale,
                            position=SpritePositionComputer.Center,
                            x_offset=0, y_offset=0, rotation=0):
        texture = pyglet.image.load(filename)
        spc = SpritePositionComputer(canvas, texture.width, texture.height,
                                     rotation)
        spc.compute(position)

        sprite = PygletSprite(model, canvas, texture, spc.x + x_offset,
                              spc.y + y_offset, rotation)
        sprite.sprite.scale = scale
        return sprite

    def create_flickering_checkerboard_sprite(self, model, canvas,
            cb_properties, position=SpritePositionComputer.Center, x_offset=0,
            y_offset=0, rotation=0, reversal=True):

        sprite = self.create_checkerboard_sprite(
            model, canvas, cb_properties, position, x_offset, y_offset,
            rotation)

        cb_properties_reversal = copy.deepcopy(cb_properties)
        if reversal:
            cb_properties_reversal.color1 = cb_properties.color2
            cb_properties_reversal.color2 = cb_properties.color1
        else:
            cb_properties_reversal.color1 = (0, 0, 0, 0)
            cb_properties_reversal.color2 = (0, 0, 0, 0)

        reversed_sprite = self.create_checkerboard_sprite(
            model, canvas, cb_properties_reversal, position, x_offset,
            y_offset, rotation)

        return FlickeringPygletSprite(sprite, reversed_sprite, canvas.batch)

    def create_checkerboard_texture(self, properties):
        """
        Creates a checkerboard image

        This takes advantage of the fact that adding two tuples together
        results in them being concatenated into a new tuple. Multiplying a
        tuple (in this case the RGB values of the pixel color) by an integer
        then results in the tuple being concatenated with itself that many
        times. This allows us to quickly build up the tuple representing the
        pixel values of the checkerboard texture.

        :param properties: an instance of a CheckerboardProperties object
        """
        tile1_texture = tuple(properties.color1) * properties.tile1_width
        tile2_texture = tuple(properties.color2) * properties.tile2_width

        n_chan = len(properties.color1)
        chan_type = 'RGBA' if n_chan == 4 else 'RGB'

        row1_texture = tuple()
        row2_texture = tuple()

        for i in range(properties.x_tiles):
            if i % 2 == 0:
                row1_texture += tile1_texture
                row2_texture += tile2_texture
            else:
                row1_texture += tile2_texture
                row2_texture += tile1_texture
        x_remain = properties.width - len(row1_texture) / n_chan
        if x_remain > 0:
            row1_texture += row1_texture[-n_chan:] * x_remain
            row2_texture += row2_texture[-n_chan:] * x_remain

        board_texture = tuple()

        for i in range(properties.y_tiles):
            if i % 2 == 0:
                board_texture += row1_texture * properties.tile1_height
            else:
                board_texture += row2_texture * properties.tile2_height
        y_remain = properties.height - len(board_texture) / n_chan
        if y_remain > 0:
            board_texture += board_texture[-properties.width:] * y_remain

        texture_data = array.array('B', board_texture).tobytes()
        image = pyglet.image.ImageData(properties.width, properties.height,
                                       chan_type, texture_data)
        texture = image.get_texture().get_transform(flip_y=True)
        return texture

    def create_checkered_box_sprite(self, model, canvas, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xoffset=0, yoffset=0, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255)):

        texture_region = self.create_checkered_box_texture_region(width, height, xfreq, yfreq, xduty, yduty, xuneven, yuneven, color_on, color_off)
        spc = SpritePositionComputer(canvas, texture_region.width, texture_region.height, rotation)
        spc.compute(position)

        return PygletSprite(model, canvas, texture_region, spc.x + xoffset, spc.y + yoffset, rotation)

    def create_checkered_box_texture_region(self, width=600, height=100, xfreq=6, yfreq=1, xduty=0.5,
        yduty=0.5, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255)):

        """
        Creates a checkerboard image
        :param size: image width and height
        :param frequencies: spatial frequencies in the x and y directions
        :param duty_cycles: ratio of 'on' to 'off' in the x and y directions
        :param uneven: is the last cycle only half-width or -height?
        :param colors: 'on' and 'off' rgb values
        """

        #print ("width, height, xfreq, yfreq, xduty, yduty, color_on, color_off", width, height, xfreq, yfreq,
        #       xduty, yduty, color_on, color_off)
        if xuneven:
            xfreq -= 0.5

        if yuneven:
            yfreq -= 0.5

        cycle_width = int(width / xfreq)
        cycle_on_width = int(cycle_width * xduty + 0.5)
        cycle_off_width = cycle_width - cycle_on_width

        cycle_height = int(height / yfreq)
        cycle_on_height = int(cycle_height * yduty + 0.5)
        cycle_off_height = cycle_height - cycle_on_height

        line_on_string = (color_on * cycle_on_width +
                          color_off * cycle_off_width) * int(xfreq)
        line_off_string = (color_off * cycle_on_width +
                           color_on * cycle_off_width) * int(xfreq)
        if xuneven:
            line_on_string += color_on * cycle_on_width
            line_off_string += color_off * cycle_on_width

        x_extra = width - len(line_on_string)/3
        if x_extra > 0:
            if xuneven:
                line_on_string += color_on * x_extra
                line_off_string += color_off * x_extra
            else:
                line_on_string += color_off * x_extra
                line_off_string += color_on * x_extra

        buf = (line_on_string * cycle_on_height +
                  line_off_string * cycle_off_height) * int(yfreq)
        if yuneven:
            buf += line_on_string * cycle_off_height

        h_extra = width*height - len(buf)/3
        if h_extra > 0:
            if yuneven:
                buf += line_on_string * (h_extra / width)
            else:
                buf += line_off_string * (h_extra / width)

        texture = pyglet.image.ImageData(width, height, 'RGB', array.array('B',buf).tobytes())
        texture_region = texture.get_texture().get_transform(flip_y=True)
        return texture_region

    def create_flickering_checkered_box_sprite(self, model, canvas, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xoffset=0, yoffset=0, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255), reversal=True):

        sprite = self.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, color_on, color_off)
        if reversal:
            reversed_sprite = self.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, color_off, color_on)
        else:
            reversed_sprite = self.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, (0,0,0), (0,0,0))
        return FlickeringPygletSprite(sprite, reversed_sprite, canvas.batch)

    def create_grid_view(self, model, canvas, icons, center_x, center_y, rect_xoffset=64, rect_yoffset=64,
           icon_width=128, icon_height=128):
        return GridView(model, canvas, icons, center_x, center_y, rect_xoffset, rect_yoffset, icon_width, icon_height)

    def create_fastpad_view(self, model, canvas):
        return FastPadView(model, canvas)

    def create_fastpad_button(self, rect, labels, actions, canvas):
        return FastPadButton(rect, labels, actions, canvas)

    def create_time_view_scope(self, model, canvas, labels=None):
        return TimeScopeView(model, canvas, labels)

    def create_frequency_scope_view(self, model, canvas, labels=None):
        return FrequencyScopeView(model, canvas, labels)

    def create_grid_view(self, state, canvas, icons):
        center_x, center_y = canvas.center()
        return GridView(state, canvas, icons, center_x, center_y)

    def create_robot_grid_view(self, state, canvas):
        return RobotGridView(state, canvas, xtiles=3, ytiles=3, tile_width=150,
                             tile_height=150)

    def create_hierarchy_grid_view(self, state, canvas):
        return HierarchyGridView(state, canvas,)

    def create_gridspeak(self, state, canvas):
        return GridSpeakView(None, state, canvas)

    def create_laser_cannon(self, state, canvas, arduino_port):
        return LaserCannonView(state, canvas, arduino_port)

    def create_quad_ssvep_views(self, stimuli, canvas, cb_properties):
        assert len(stimuli.stimuli) == 4

        views = list()

        fs1 = self.create_flickering_checkerboard_sprite(
            stimuli.stimuli[0], canvas, cb_properties,
            position=SpritePositionComputer.Center, y_offset=360, reversal=False)
        views.append(fs1)

        fs2 = self.create_flickering_checkerboard_sprite(
            stimuli.stimuli[1], canvas, cb_properties,
            position=SpritePositionComputer.Center, y_offset=-360, reversal=False)
        views.append(fs2)

        fs3 = self.create_flickering_checkerboard_sprite(
            stimuli.stimuli[2], canvas, cb_properties,
            position=SpritePositionComputer.Center, x_offset=-360,
            reversal=False)
        views.append(fs3)

        fs4 = self.create_flickering_checkerboard_sprite(
            stimuli.stimuli[3], canvas, cb_properties,
            position=SpritePositionComputer.Center, x_offset=360,
            reversal=False)
        views.append(fs4)

        return views

    def create_single_ssvep_view(self, stimulus, canvas, cb_properties):
        views = list()
        fs = self.create_flickering_checkerboard_sprite(stimulus, canvas,
            cb_properties, SpritePositionComputer.Center, reversal=False)
        views.append(fs)

        return views

    def create_single_msequence_view(self, stimulus, canvas, cb_properties):
        views = list()
        fs = self.create_flickering_checkerboard_sprite(stimulus, canvas,
            cb_properties, SpritePositionComputer.Center, reversal=True)
        views.append(fs)

        return views

    def create_quad_msequence_view(self, stimuli, canvas, cb_properties):
        offset = 360  # for online session
        #offset = 270  # for offline covert session
        fs1 = self.create_flickering_checkerboard_sprite(stimuli[0], canvas,
            cb_properties, SpritePositionComputer.Center, y_offset=offset,
            reversal=False)
        fs2 = self.create_flickering_checkerboard_sprite(stimuli[1], canvas,
            cb_properties, SpritePositionComputer.Center, y_offset=-offset,
            reversal=False)
        fs3 = self.create_flickering_checkerboard_sprite(stimuli[2], canvas,
            cb_properties, SpritePositionComputer.Center, x_offset=-offset,
            reversal=False)
        fs4 = self.create_flickering_checkerboard_sprite(stimuli[3], canvas,
            cb_properties, SpritePositionComputer.Center, x_offset=offset,
            reversal=False)
        # fixation = PygletTextLabel(UnlockState(True), canvas, '+',
        #                            *canvas.center())
        
        return [fs1, fs2, fs3, fs4]

    def create_dual_overlapping_cvep_view(self, stimuli, canvas,
                                          cb_properties):
        fs1 = self.create_flickering_checkerboard_sprite(stimuli[0], canvas,
            cb_properties[0], SpritePositionComputer.Center, reversal=False, x_offset=6, y_offset=6)
        fs2 = self.create_flickering_checkerboard_sprite(stimuli[1], canvas,
            cb_properties[1], SpritePositionComputer.Center, reversal=False, x_offset=-6, y_offset=-6)

        return [fs1, fs2]

    def create_dual_image_cvep_view(self, stimuli, canvas, filenames):
        fs1 = self.create_image_sprite(stimuli[0], canvas,
            filenames[0], SpritePositionComputer.Center, x_offset=-400)
        fs2 = self.create_image_sprite(stimuli[1], canvas,
            filenames[1], SpritePositionComputer.Center, x_offset=400)

        return [fs1, fs2]
       

    def create_robot_controller_view(self, model, canvas):
        return RobotView(model, canvas)
