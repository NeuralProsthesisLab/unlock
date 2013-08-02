
import pyglet


class UnlockView(object):
    def __init__(self):
        super(UnlockView, self).__init__()
        
    def drawRect(self, x_offset, y_offset, width, height, batch, color=(255,255,255), fill=False,
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
            
        self.vertex_list = batch.add(4, mode, group,
            ('v2f', (x_offset, y_offset,
                     x_offset + width, y_offset,
                     x_offset + width, y_offset + height,
                     x_offset, y_offset + height)),
            ('c3B', color*4))
        return self.vertex_list