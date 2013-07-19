import pyglet
import array

from math import cos, sin, radians
from unlock.util import switch
   

class PygletSprite(object):
    def __init__(self, model, screen_desc, image, x, y, rotation):
        self.model = model
        self.screen_desc = screen_desc
        
        image.anchor_x = image.width / 2
        image.anchor_y = image.height / 2
        
        self.sprite = pyglet.sprite.Sprite(image, batch=self.screen_desc.batch)
        self.sprite.rotation = rotation
        self.sprite.x = x
        self.sprite.y = y
        self.sprite.visible = False
        
    def render(self):
        self.sprite.visible = self.model.state()
        
    @staticmethod
    def create_image_sprite(model, screen_desc, filename, rotation):
        abstract_image = pyglet.image.load(filename)
        return PygletSprite(model, screen_desc, abstract_image, rotation)
           
    @staticmethod
    def create_checkered_box_texture_region(width=600, height=100, xfreq=6, yfreq=1,
                xduty=0.5, yduty=0.5, xuneven=False, yuneven=False,
                color_on=(0,0,0), color_off=(255,255,255)):
        """
        Creates a checkerboard image
        :param size: image width and height
        :param frequencies: spatial frequencies in the x and y directions
        :param duty_cycles: ratio of 'on' to 'off' in the x and y directions
        :param uneven: is the last cycle only half-width or -height?
        :param colors: 'on' and 'off' rgb values
        """        
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
                
        buffer = (line_on_string * cycle_on_height +
                  line_off_string * cycle_off_height) * int(yfreq)
        if yuneven:
            buffer += line_on_string * cycle_off_height
                
        h_extra = width*height - len(buffer)/3
        if h_extra > 0:
            if yuneven:
                buffer += line_on_string * (h_extra / width)
            else:
                buffer += line_off_string * (h_extra / width)
                
        texture = pyglet.image.ImageData(width, height, 'RGB',
                                      array.array('B',buffer).tostring())
        texture_region = texture.get_texture().get_transform(flip_y=True)
        return texture_region
            
    @staticmethod
    def create_checkered_box_sprite(model, screen_desc, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255)):
            
        texture_region = PygletSprite.create_checkered_box_texture_region(width, height, xfreq, yfreq, xduty, yduty, xuneven, yuneven, color_on, color_off)
            
        spc = SpritePositionComputer(screen_desc.width, screen_desc.height, texture_region.width, texture_region.height, rotation)
        spc.compute(position)
           
        return PygletSprite(model, screen_desc, texture_region, spc.x, spc.y, rotation)
            
            
class FlickeringPygletSprite(PygletSprite):
    def __init__(self, sprite, reversed_sprite, batch):
        self.sprite = sprite
        self.reversed_sprite = reversed_sprite
        self.batch = batch
        
    def render(self):
        state = self.sprite.model.state()
        self.sprite.sprite.visible = state
        self.reversed_sprite.sprite.visible = not state
        self.batch.draw()
        
    @staticmethod
    def create_flickering_checkered_box_sprite(model, screen_desc, position=SpritePositionComputer.Center, rotation=0, width=600, height=100, xfreq=6, yfreq=1,
            xduty=0.5, yduty=0.5, xuneven=False, yuneven=False, color_on=(0,0,0), color_off=(255,255,255)):
            
        sprite = PygletSprite.create_checkered_box_sprite(model, screen_desc, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xuneven, yuneven, color_on, color_off)
        reversed_sprite = PygletSprite.create_checkered_box_sprite(model, screen_desc, position, rotation, width, height, xfreq, yfreq,
                                                          xduty, yduty, xuneven, yuneven, color_off, color_on)
            
        return FlickeringPygletSprite(sprite, reversed_sprite, screen_desc.batch)
            
           
class SpritePositionComputer(object):
    North=0
    NorthEast=1
    East=2
    SouthEast=3
    South=4
    SouthWest=5
    West=6
    NorthWest=7
    Center=8
    
    def __init__(self, screen_width, screen_height, image_width, image_height, rotation):
        self.width = screen_width
        self.height = screen_height
        self.angle = abs(radians(rotation))
        self.box_width = (image_width * cos(self.angle) + image_height * sin(self.angle))
        self.box_height = (image_width * sin(self.angle) + image_height * cos(self.angle))
        self.center()
        
    def compute(self, position):
        for case in switch(position):
            if case(SpritePositionComputer.North):
                self.north()
                break
            if case(SpritePositionComputer.NorthEast):
                self.northeast()
                break
            if case(SpritePositionComputer.East):
                self.east()
                break
            if case(SpritePositionComputer.SouthEast):
                self.southeast()
                break
            if case(SpritePositionComputer.South):
                self.south()
                break
            if case(SpritePositionComputer.SouthWest):
                self.southwest()
                break
            if case(SpritePositionComputer.West):
                self.west()
                break
            if case(SpritePositionComputer.Center):
                self.center()
                break
            if case ():
                self.center()
                break
                
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
         
            