import array

import pyglet

from unlock.view import PygletSprite


class CheckerboardSprite(PygletSprite):
    def __init__(self, model, canvas, properties):
        self.properties = properties
        texture = self.generate_texture()

        super(CheckerboardSprite, self).__init__(model, canvas, texture,
                                                 )

    def generate_texture(self):
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
        check1_texture = self.properties.color1 * self.properties.check1_width
        check2_texture = self.properties.color2 * self.properties.check2_width

        row1_texture = tuple()
        row2_texture = tuple()

        for i in range(self.properties.x_checks):
            if i % 2 == 0:
                row1_texture += check1_texture
                row2_texture += check2_texture
            else:
                row1_texture += check2_texture
                row2_texture += check1_texture
        x_remain = self.properties.width - len(row1_texture) / 3
        if x_remain > 0:
            row1_texture += row1_texture[-3:] * x_remain
            row2_texture += row2_texture[-3:] * x_remain

        board_texture = tuple()

        for i in range(self.properties.y_checks):
            if i % 2 == 0:
                board_texture += row1_texture * self.properties.check1_height
            else:
                board_texture += row2_texture * self.properties.check2_height
        y_remain = self.properties.height - len(board_texture) / 3
        if y_remain > 0:
            board_texture += board_texture[-self.properties.width:] * y_remain

        texture_data = array.array('B', board_texture).tobytes()
        image = pyglet.image.ImageData(
            self.properties.width, self.properties.height, 'RGB', texture_data)
        texture = image.get_texture().get_transform(flip_y=True)
        return texture


class CheckerboardProperties(object):
    """
    An object that collects all the properties used to generate a
    checkerboard sprite.

    anchor and offsets refer specifically to the sprite and don't need to be here

    :param width: width of the checkerboard in pixels
    :param height: height of the checkerboard in pixels
    :param anchor: anchor position on the screen (SpritePositionComputer)
    :param rotation: degrees rotated counterclockwise
    :param x_offset: offset from anchor position in pixels
    :param y_offset: offset from anchor position in pixels
    :param x_checks: total number of horizontal checks
    :param y_checks: total number of vertical checks
    :param x_ratio: width ratio between alternating checks
    :param y_ratio: height ratio between alternating checks
    :param color1: RGB color of one set of checks
    :param color2: RGB color of the other set of checks
    """
    def __init__(self, width=300, height=300, anchor=None, rotation=0,
                 x_offset=0, y_offset=0, x_checks=4, y_checks=4, x_ratio=1,
                 y_ratio=1, color1=(0, 0, 0), color2=(255, 255, 255)):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_checks = x_checks
        self.y_checks = y_checks
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.color1 = color1
        self.color2 = color2

        # Computed properties
        pair_width = int(width / x_checks * 2)
        self.check1_width = int(pair_width * (x_ratio / (x_ratio + 1)))
        self.check2_width = pair_width - self.check1_width

        pair_height = int(height / y_checks * 2)
        self.check1_height = int(pair_height * (y_ratio / (y_ratio + 1)))
        self.check2_height = pair_height - self.check1_height