#!/usr/bin/env python

import sys

import pyglet
from pyglet.gl import *

class OscillatingImage(object):
    def __init__(self, filename):
        self.filename = filename
        self.window = pyglet.window.Window(visible=False, resizable=True)
        self.window.event(self.on_draw)
        pyglet.clock.schedule_interval(self.update, 5)
        self.image_drawn = True
        self.setup_target()
    def setup_target(self):
        img = pyglet.image.load(self.filename).get_texture(rectangle=True)
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        checks = pyglet.image.create(32, 32, pyglet.image.CheckerImagePattern())
        self.background = pyglet.image.TileableTexture.create_for_image(checks)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)    
        self.window.width = img.width
        self.window.height = img.height
        self.window.set_visible()
        self.img = img
    def start(self):
        pyglet.app.run()
    def on_draw(self):
        self.background.blit_tiled(0, 0, 0, self.window.width, self.window.height)
        if self.image_drawn:
            self.draw_image()
            
    def draw_image(self):
        self.img.blit(self.window.width // 2, self.window.height // 2, 0)

    def update(self, dt):
        if self.image_drawn:
            self.image_drawn = False
            self.setup_target()
        else:
            self.image_drawn = True
            self.setup_target()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print __doc__
        sys.exit(1)
    oimage = OscillatingImage(sys.argv[1])
    oimage.start()
