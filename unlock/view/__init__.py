from unlock.view.pyglet_sprite import *
from unlock.view.pyglet_text import *
from unlock.view.view import *
from unlock.view.grid import *
from unlock.view.fastpad_view import *
from unlock.view.scope_view import *

class UnlockViewFactory(object):

    def create_image_pyglet_sprit(model, canvas, filename, x=0, y=0, rotation=0):
        abstract_image = pyglet.image.load(filename)
        return PygletSprite(model, canvas, abstract_image, int(x), int(y), rotation)

    def create_checkered_box_sprite(model, canvas, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xoffset=0, yoffset=0, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255)):

        texture_region = UnlockViewFactory.create_checkered_box_texture_region(width, height, xfreq, yfreq, xduty, yduty, xuneven, yuneven, color_on, color_off)

        spc = SpritePositionComputer(canvas, texture_region.width, texture_region.height, rotation)
        spc.compute(position)

        return PygletSprite(model, canvas, texture_region, spc.x + xoffset, spc.y + yoffset, rotation)

    def create_checkered_box_texture_region(width=600, height=100, xfreq=6, yfreq=1, xduty=0.5,
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

    def create_flickering_checkered_box_sprite(model, canvas, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xoffset=0, yoffset=0, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255), reversal=True):

        sprite = UnlockViewFactory.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, color_on, color_off)
        if reversal:
            reversed_sprite = UnlockViewFactory.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, color_off, color_on)
        else:
            reversed_sprite = UnlockViewFactory.create_checkered_box_sprite(model, canvas, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xoffset, yoffset, xuneven, yuneven, (0,0,0), (0,0,0))
        return FlickeringPygletSprite(sprite, reversed_sprite, canvas.batch)

    def create_grid_view(model, canvas, icons, center_x, center_y, rect_xoffset=64, rect_yoffset=64,
           icon_width=128, icon_height=128):
        return GridView(model, canvas, icons, center_x, center_y, rect_xoffset, rect_yoffset, icon_width, icon_height)

    def create_fast_pad_view(model, canvas):
        return FastPadView(model, canvas)

    def create_fastpad_button(rect, labels, actions, canvas):
        return FastPadButton(rect, labels, actions, canvas)

    def create_time_view_scope( model, canvas, labels=None):
        return TimeScopeView(model, canvas, labels)

    def create_frequency_scope_view(model, canvas, labels=None):
        return FrequencyScopeView(model, canvas, labels)

    def create_dashboard_grid(self):

        grid_view = GridView(grid_state, canvas, icons, center_x, center_y)

    def create_quad_ssvep_views(self, stimuli, canvas, width=500, height=100, horizontal_blocks=5, vertical_blocks=1,
            color=[0,0,0], color1=[255,255,255]):

        assert len(stimuli.stimulus) == 4

        views = []

        fs = self.view_factory.create_flickering_checkered_box_sprite(stimuli.stimulus[0], canvas,
            SpritePositionComputer.North, width=width, height=height, xfreq=horizontal_blocks, yfreq=vertical_blocks,
            color_on=color, color_off=color1, reversal=False)

        fs1 = self.view_factory.create_flickering_checkered_box_sprite(stimuli.stimulus[1], canvas,
            SpritePositionComputer.South, width=width, height=height, xfreq=horizontal_blocks, yfreq=vertical_blocks,
            color_on=color, color_off=color1, reversal=False)

        fs2 = self.view_factory.create_flickering_checkered_box_sprite(stimuli.stimulus[2], canvas,
            SpritePositionComputer.West, width=width, height=height, xfreq=horizontal_blocks, yfreq=vertical_blocks,
            color_on=color, color_off=color1, reversal=False, rotation=90)

        fs3 = self.view_factory.create_flickering_checkered_box_sprite(stimuli.stimulus[3], canvas,
            SpritePositionComputer.East, width=width, height=height, xfreq=horizontal_blocks, yfreq=vertical_blocks,
            color_on=color, color_off=color1, reversal=False, rotation=90)

        views.append(fs)
        views.append(fs1)
        views.append(fs2)
        views.append(fs3)
