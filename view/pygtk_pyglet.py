#!/usr/bin/python

import os, os.path, sys, time
from math import *
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pyglet
from pyglet.gl import *

if sys.platform in ('win32','cygwin'):
  from pyglet.window.win32 import _user32
  from pyglet.gl import wgl
elif sys.platform == 'linux2':
  from pyglet.image.codecs.gdkpixbuf2 import gdk
  from pyglet.gl import glx

class Torus(object):
  def __init__(self, radius, inner_radius, slices, inner_slices):
    # Create the vertex and normal arrays.
    vertices = []
    normals = []

    u_step = 2 * pi / (slices - 1)
    v_step = 2 * pi / (inner_slices - 1)
    u = 0.
    for i in range(slices):
      cos_u = cos(u)
      sin_u = sin(u)
      v = 0.
      for j in range(inner_slices):
        cos_v = cos(v)
        sin_v = sin(v)

        d = (radius + inner_radius * cos_v)
        x = d * cos_u
        y = d * sin_u
        z = inner_radius * sin_v

        nx = cos_u * cos_v
        ny = sin_u * cos_v
        nz = sin_v

        vertices.extend([x, y, z])
        normals.extend([nx, ny, nz])
        v += v_step
      u += u_step

    # Create ctypes arrays of the lists
    vertices = (GLfloat * len(vertices))(*vertices)
    normals = (GLfloat * len(normals))(*normals)

    # Create a list of triangle indices.
    indices = []
    for i in range(slices - 1):
      for j in range(inner_slices - 1):
        p = i * inner_slices + j
        indices.extend([p, p + inner_slices, p + inner_slices + 1])
        indices.extend([p,  p + inner_slices + 1, p + 1])
    indices = (GLuint * len(indices))(*indices)

    # Compile a display list
    self.list = glGenLists(1)
    glNewList(self.list, GL_COMPILE)

    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glNormalPointer(GL_FLOAT, 0, normals)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT,
indices)
    glPopClientAttrib()

    glEndList()

  def draw(self):
    glCallList(self.list)


class GtkGlDrawingArea(gtk.DrawingArea):
  config=None
  context=None

  def __init__(self):
    self.gl_initialized = 0
    self.get_config()
    gtk.DrawingArea.__init__(self)
    self.set_double_buffered(0)
    self.connect('expose-event', self.expose)
    self.connect('configure-event', self.configure)

  def get_config(self):
    if not self.config:
      platform = pyglet.window.get_platform()
      self.display = platform.get_default_display()
      self.screen = self.display.get_screens()[0]

      for template_config in [
        Config(double_buffer=True, depth_size=32),
        Config(double_buffer=True, depth_size=24),
        Config(double_buffer=True, depth_size=16)]:
        try:
          self.config = self.screen.get_best_config(template_config)
          break
        except pyglet.window.NoSuchConfigException:
          pass

      if not self.config:
        raise pyglet.window.NoSuchConfigException(
            'No standard config is available.')

      if not self.config.is_complete():
        print 'not complete'
        self.config = self.screen.get_best_config(self.config)

      print self.config.get_gl_attributes()

      if not self.context:
        self.context = self.config.create_context(pyglet.gl.current_context)

  def setup(self):
    # One-time GL setup
    glClearColor(0, 0, 0, 1)
    glColor3f(1, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    # Define a simple function to create ctypes arrays of floats:
    def vec(*args):
      return (GLfloat * len(args))(*args)

    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5,
0, 0.3, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
    if sys.platform in ('win32', 'cygwin'):
      self.lowerlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='Arial',
                                          x=5, y=20)
      self.upperlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='Arial',
                                          x=20, y=20)
    else:
      self.lowerlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='DejaVu Sans Mono',
                                          x=5, y=20)
      self.upperlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='DejaVu Sans Mono',
                                          x=20, y=20)
    print 'end setup'

  def switch_to(self):
    if sys.platform == 'darwin':
      agl.aglSetCurrentContext(self._agl_context)
      _aglcheck()
    elif sys.platform in ('win32', 'cygwin'):
      self._dc = _user32.GetDC(self.window.handle)
      self.context._set_window(self)
      wgl.wglMakeCurrent(self._dc, self.context._context)
    else:
      glx.glXMakeCurrent(self.config._display, self.window.xid,
self.context._context)
    self.context.set_current()
    gl_info.set_active_context()
    glu_info.set_active_context()

  def flip(self):
    if sys.platform == 'darwin':
      agl.aglSwapBuffers(self._agl_context)
      _aglcheck()
    elif sys.platform in ('win32', 'cygwin'):
      wgl.wglSwapLayerBuffers(self._dc, wgl.WGL_SWAP_MAIN_PLANE)
    else:
      glx.glXSwapBuffers(self.config._display, self.window.xid)

  def configure(self, d, event):
    width = d.allocation.width
    height = d.allocation.height
    if width > 1:
      # make the context current
      # and setup opengl
      #
      # **** this only can be with the window realized ****
      #
      self.switch_to()
      if not self.gl_initialized:
        self.setup()
        self.gl_initialized = 1
      glViewport(0, 0, width, height)
    return 0

  def expose(self, d, event):
    global rx, ry, rz, dt
    width = d.allocation.width
    height = d.allocation.height
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60., width / float(height), .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -4)
    glRotatef(rz, 0, 0, 1)
    glRotatef(ry, 0, 1, 0)
    glRotatef(rx, 1, 0, 0)
    glEnable(GL_LIGHTING)
    glColor3f(1, 0, 0)
    torus.draw()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 1)
    self.lowerlabel.text = 'Rx %.2f Ry %.2f Rz %.2f' % (rx, ry, rz)
    self.lowerlabel.draw()
    self.upperlabel.text = time.strftime('Now is %H:%M:%S')
    self.upperlabel.x = width - self.upperlabel.content_width -5
    self.upperlabel.y = height - self.upperlabel.content_height
    self.upperlabel.draw()
    if self.config.double_buffer:
      self.flip()
    else:
      gl.glFlush()
    return 0

def timeout():
  global rx, ry, rz, dt
  rx += dt * 1
  ry += dt * 80
  rz += dt * 30
  rx %= 360
  ry %= 360
  rz %= 360
  darea.queue_draw()
  return 1

def click(b, what):
  print '%s clicked' % what


torus = Torus(1, 0.3, 50, 30)
rx = ry = rz = 0
dt = 0.01

mw = gtk.Window()
mw.connect('destroy', gtk.main_quit)
darea = GtkGlDrawingArea()
darea.set_size_request(500, 500)
vbox = gtk.VBox()
vbox.set_homogeneous(0)
mw.add(vbox)
b = gtk.Button('Upper')
b.connect('clicked', click, 'Upper')
vbox.pack_start(b, 0, 0)
vbox.pack_start(darea, 1, 1)
b = gtk.Button('Lower')
b.connect('clicked', click, 'Lower')
vbox.pack_end(b, 0, 0)
mw.show_all()
# set refresh timing
gobject.timeout_add(20, timeout)
gtk.main()
