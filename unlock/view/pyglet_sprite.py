
import pyglet
import array
import logging

from unlock.view.view import UnlockView
from math import cos, sin, radians
from unlock.util import switch


class SpritePositionComputer(object):
    North = 0
    NorthEast = 1
    East = 2
    SouthEast = 3
    South = 4
    SouthWest = 5
    West = 6
    NorthWest = 7
    Center = 8

    def __init__(self, canvas, image_width, image_height, rotation):
        self.width = canvas.width
        self.height = canvas.height
        self.x0 = canvas.x
        self.y0 = canvas.y
        self.angle = abs(radians(rotation))
        self.box_width = (image_width * cos(self.angle) + image_height * sin(self.angle))
        self.box_height = (image_width * sin(self.angle) + image_height * cos(self.angle))
        self.center()
        
    def compute(self, position):
        {
            SpritePositionComputer.North: self.north,
            SpritePositionComputer.NorthEast: self.northeast,
            SpritePositionComputer.East: self.east,
            SpritePositionComputer.SouthEast: self.southeast,
            SpritePositionComputer.South: self.south,
            SpritePositionComputer.SouthWest: self.southwest,
            SpritePositionComputer.West: self.west,
            SpritePositionComputer.NorthWest: self.northwest,
            SpritePositionComputer.Center: self.center,
        }.get(position, self.center)()
#        print("X, y", self.x, self.y)
#        print("X, y", self.x0, self.y0)
#        print("width, height", self.width, self.height)
#        print("box_width, box_height", self.box_width, self.box_height)
        self.x += self.x0
        self.y += self.y0
                
    def north(self):
        self.x = self.width / 2
        self.y = self.height - self.box_height / 2        

    def northeast(self):
        self.x = self.width - self.box_width / 2
        self.y = self.height - self.box_height / 2
        
    def east(self):
        self.x = self.width - self.box_width / 2
        self.y = self.height / 2        
        
    def southeast(self):
        self.x = self.width - self.box_width / 2
        self.y = self.box_height / 2
        
    def south(self):
        self.x = self.width / 2
        self.y = self.box_height / 2
        
    def southwest(self):
        self.x = self.box_width / 2
        self.y = self.box_height / 2
        
    def west(self):
        self.x = self.box_width / 2
        self.y = self.height / 2
        
    def northwest(self):
        self.x = self.box_width / 2
        self.y = self.height  - self.box_height/2
        
    def center(self):
        self.x = self.width / 2
        self.y = self.height / 2
            
           
class PygletSprite(UnlockView):
    def __init__(self, model, canvas, image, x, y, rotation):
        self.model = model
        self.canvas = canvas
        
        image.anchor_x = int(image.width / 2)
        image.anchor_y = int(image.height / 2)
        
        self.sprite = pyglet.sprite.Sprite(image, batch=self.canvas.batch)
        self.sprite.rotation = rotation
        self.sprite.x = x
        self.sprite.y = y
        self.sprite.visible = False
        self.logger = logging.getLogger(__name__)
        
    def render(self):
        self.sprite.visible = self.model.get_state()


class FlickeringPygletSprite(PygletSprite):
    def __init__(self, sprite, reversed_sprite, batch):
        self.sprite = sprite
        self.reversed_sprite = reversed_sprite
        self.batch = batch
        self.logger = logging.getLogger(__name__)        
        
    def render(self):
        state = self.sprite.model.get_state()
        if state == None:
            self.sprite.sprite.visible = False
            self.reversed_sprite.visible = False
        else:
            #print("FlickeringPygletSprite, x,y = ", self.sprite.sprite.x, self.sprite.sprite.y, " rotation ", self.sprite.sprite.rotation, " visible = ", state)
            self.sprite.sprite.visible = state
            self.reversed_sprite.sprite.visible = not state
        #print('flickeringsprit state = ', state)

