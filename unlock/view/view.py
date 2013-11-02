
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

    def drawGrid(self, x_offset, y_offset, rows, columns, tile_width,
                 tile_height, batch, color=(255, 255, 255), group=None):
        mode = pyglet.gl.GL_LINES
        width = tile_width*columns
        height = tile_height*rows

        self.verticies = []
        for i in range(rows+1):
            self.verticies.append(batch.add(2, mode, group,
                ('v2f', (x_offset, y_offset + i*tile_height,
                         x_offset + width, y_offset + i*tile_height)),
                ('c3B', color*2)))
        for i in range(columns+1):
            self.verticies.append(batch.add(2, mode, group,
                ('v2f', (x_offset + i*tile_width, y_offset,
                         x_offset + i*tile_width, y_offset + height)),
                ('c3B', color*2)))
        return self.verticies
        
    def drawText(self, text, x, y, batch, font='Helvetica', size=48,
                 color=(255,255,255,255), group=None, xoffset=0, yoffset=0):
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
            font_name=font, font_size=size, x=xoffset + x, y=yoffset + y,
            anchor_x='center', anchor_y='center', color=color,
            group=group, batch=batch)
            
    def drawLine(self, x1, y1, x2, y2, canvas, color=(255,255,255), group=None):
        """
        Draws a line between two points on the screen
        
        :param x1: x-coordinate of first point (Pixels from left)
        :param y1: y-coordinate of first point (Pixels from bottom)
        :param x2: x-coordinate of second point (Pixels from left)
        :param y2: y-coordinate of second point (Pixels from bottom)
        :param color: Color of line. Tuple of length three.
        :param group: Batch group
        """
        return canvas.batch.add(2, pyglet.gl.GL_LINES, group,
            ('v2f', (canvas.x+x1, canvas.y+y1, canvas.x+x2, canvas.y+y2)),
            ('c3B', color*2))

    def drawLinePlot(self, vertices, canvas, color=(255,255,255), group=None):
        """
        Given a set of vertices, will plot lines between each vertices in the
        list

        :param vertices: list of vertices to be plotted.
        :param color: Color of Line plot. Tuple of length three
        :param group: batch group
        """
        data_points = int(len(vertices) / 2)
        # create points - 1 line segments
        # both endpoints of each segment need to be specified, so all but the
        # two endpoints of the entire trace need to be repeated
        vertices[::2] = [x + canvas.x for x in vertices[::2]]
        vertices[1::2] = [y + canvas.y for y in vertices[1::2]]
        line_segments = vertices[0:4]  # (x0, y0, x1, y1)
        for i in range(1, data_points-1):
            line_segments.extend([vertices[i*2], vertices[i*2+1],
                                  vertices[(i+1)*2], vertices[(i+1)*2+1]])
        plot_points = int(len(line_segments) / 2)

        return canvas.batch.add(plot_points, pyglet.gl.GL_LINES, group,
            ('v2f', line_segments),
            ('c3B', color*plot_points))