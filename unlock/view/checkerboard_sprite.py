class CheckerboardProperties(object):
    """
    An object that collects all the properties used to generate a
    checkerboard sprite.

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