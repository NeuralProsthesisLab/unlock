import pyglet

class Screen(object):
    def __init__(self, x, y, width, height):

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = pyglet.graphics.Batch()

    def get_offset(self):
        """Returns the offset of the screen off the window"""
        return self.x, self.y

    def get_size(self):
        """Returns height and width of screen """
        return self.width, self.height

    def get_width(self):
        """Returns width of screen """
        return self.width

    def get_height(self):
        """Returns height of screen """
        return self.height

    def get_center(self):
        """Returns the center of the screen"""
        return self.width / 2, self.height / 2

    def copy(self):
        """Returns another screen object with the same dimensions"""
        return Screen(self.x, self.y, self.width, self.height)

    def drawText(self, text, x, y, font='Helvetica', size=48,
                 color=(255,255,255,255), group=None):
        """
        Draws text at a specific point on the screen

        :param text: Text to display
        :param x: x-coordinate of center of text(Pixels from left)
        :param y: y-coordinate of center of text(Pixels from bottom)
        :param font: Font of text
        :param size: Size of text
        :param color: Color of text. Tuple of length four.
        :param group: Batch group
        """
        if len(color) == 3:
            color = color + (255,)

        return pyglet.text.Label(text,
            font_name=font, font_size=size, x=self.x + x, y=self.y + y,
            anchor_x='center', anchor_y='center', color=color,
            group=group, batch=self.batch)

    def drawLine(self, x1, y1, x2, y2, color=(255,255,255), group=None):
        """
        Draws a line between two points on the screen

        :param x1: x-coordinate of first point (Pixels from left)
        :param y1: y-coordinate of first point (Pixels from bottom)
        :param x2: x-coordinate of second point (Pixels from left)
        :param y2: y-coordinate of second point (Pixels from bottom)
        :param color: Color of line. Tuple of length three.
        :param group: Batch group
        """
        return self.batch.add(2, pyglet.gl.GL_LINES, group,
            ('v2f', (self.x + x1, self.y + y1, self.x + x2, self.y + y2)),
            ('c3B', color*2))

    def drawLinePlot(self, vertices, color=(255,255,255), group=None):
        """
        Given a set of vertices, will plot lines between each vertices in the list

        :param vertices: list of vertices to be plotted.
        :param color: Color of Line plot. Tuple of length three
        :param group: batch group
        """
        points = len(vertices) / 2
        vertices[::2] = [i + self.x for i in vertices[::2]]
        vertices[1::2] = [i + self.y for i in vertices[1::2]]
        lines = vertices[0:4]
        for i in range(1,points-1):
            lines.extend([vertices[i*2],vertices[i*2+1],
                          vertices[(i+1)*2],vertices[(i+1)*2+1]])
        points = len(lines) / 2
#        first = vertices[0:2]
#        vertices.insert(0,first[0])
#        vertices.insert(1,first[1])
#        vertices.extend(vertices[-2:])

        line = self.batch.add(points, pyglet.gl.GL_LINES, group,
            ('v2f', lines),
#            ('c3B', (0,255,0)+color*points+(0,255,0)))
            ('c3B', color*points))
        return LinePlot(line, self.y)

    def drawRect(self, x, y, width, height, color=(255,255,255), fill=False,
                 group=None):
        """
        Draws a rectangle. Either just the frame, or a filled in shape.

        :param x: x-ccordinate of leftmost vertice. In unit pixels from Left
        :param y: y-cooridnate of bottommost vertice. In unit pixels from Bottom
        :param width: width of rectangle. Unit pixels
        :param height: height of rectangle. Unit pixels
        :param color: color of rectangle. Tuple of length three.
        :param fill: Toggle whether the rectangle should be filled or left as a frame
        :param group: batch group
        """
        mode = pyglet.gl.GL_LINE_LOOP
        if fill:
            mode = pyglet.gl.GL_QUADS

        return self.batch.add(4, mode, group,
            ('v2f', (self.x + x, self.y + y,
                     self.x + x + width, self.y + y,
                     self.x + x + width, self.y + y + height,
                     self.x + x, self.y + y + height)),
            ('c3B', color*4))

    def loadSprite(self, filename, x, y):
        """
        Load an image for use as an image

        :param filename: name and location of file to use
        :param x: x-coordinate of center of sprite. In unit pixels from left
        :param y: y-coordinate of center of sprite. In unit pixels from bottom
        """
        image = pyglet.image.load(filename)
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        return pyglet.sprite.Sprite(image, x=self.x + x, y=self.y + y,
            batch=self.batch)

    def addGroup(self, order=0):
        "adds a group to the list of groups"
        return pyglet.graphics.OrderedGroup(order)

class LinePlot(object):
    def __init__(self, line, y_offset):
        self.line = line
        self.y = y_offset

    def updateData(self, y_data, offset=0):
        points = len(y_data)
        lines = y_data[0:2]
        for i in range(1,points-1):
            lines.extend([y_data[i],y_data[i+1]])
        self.line.vertices[1::2] = [i + self.y for i in lines]
#        self.line.vertices[1] = y_data[0] + self.y
#        self.line.vertices[3:-2:2] = [i + self.y for i in y_data]
#        self.line.vertices[-1] = y_data[-1] + self.y_data