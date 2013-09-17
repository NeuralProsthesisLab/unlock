#import pygame
#from pygame.transform import scale
import pyglet
import asimov
import json
import time
import cStringIO
from core import UnlockApplication

#from robot import FrameGrabber, MotorController

class FrameGrabber(asimov.AsimovReader):
    """
    Asimov interface class to get and prepare the images streaming from the
    robot camera
    """
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace, asimov.ROBOT_VIDEO, 0.5)
        self.frame = pyglet.image.load("resource/error.jpg")

    def process(self, value):
        try:
            buffer = cStringIO.StringIO()
            buffer.write(value)
            buffer.reset()
            self.frame = pyglet.image.load('frame.jpg', buffer)
            #self.frame = self.frame.get_texture().get_transform(flip_y=True)
            #image.get_texture()
            #self.frame = image# image.get_texture().get_transform(flip_y=True).get_image_data()
        except Exception as e:
            print "Video process error: " + str(e)


class MotorController(asimov.AsimovWriter):
    """
    Asimov interface class to set motor commands
    """
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace)
        self.commands = None
        self.program = []

    def process(self):
        if len(self.program) > 0:
            if self.program[0][0] <= time.time():
                cmd = self.program.pop(0)
                self.commands = cmd[1]

        if self.commands is not None:
            try:
                self.set(asimov.MOTOR_OUT, json.dumps(self.commands))
            except Exception as e:
                pass
            self.commands = None

class RobotDriver(UnlockApplication):

    name = "Robot Driver"

    def __init__(self, screen, namespace, video=None, motor=None):
        super(self.__class__, self).__init__(screen)
        self.namespace = namespace
        self.video = FrameGrabber(namespace)
        self.motor = MotorController(namespace)
        self.frame = pyglet.sprite.Sprite(self.video.frame, (screen.get_width() - 2*self.video.frame.width)/2 + screen.x,
            (screen.get_height() - 2*self.video.frame.height)/2 + screen.y,
            batch=screen.batch)
        self.frame.scale = 2

        self.video.start()
        self.motor.start()

    def quit(self):
        self.video.stop()
        self.motor.stop()

    def update(self, dt, decision, selection):
        self.frame.image = self.video.frame.get_texture().get_transform(flip_y=True)
        self.frame.y = self.screen.y + 660

        if decision == 1:
            if self.namespace == "morse":
                self.motor.commands = {'left': {'w': 0, 'v': 1}}
            else:
                self.motor.commands = {'left':50,'right':50}
        elif decision == 2:
            #self.close()
            if self.namespace == "morse":
                self.motor.commands = {'left': {'w': 0, 'v': -1}}
            else:
                self.motor.commands = {'left':-50,'right':-50}
        elif decision == 3:
            if self.namespace == "morse":
                self.motor.commands = {'left': {'w': 1, 'v': 0}}
            else:
                self.motor.commands = {'left':-50,'right':50}
        elif decision == 4:
            if self.namespace == "morse":
                self.motor.commands = {'left': {'w': -1, 'v': 0}}
            else:
                self.motor.commands = {'left':50,'right':-50}
        if selection:
            if self.namespace == "morse":
                self.motor.commands = {'left': {'w': 0, 'v': 0}}
            else:
                self.motor.commands = {'left':0,'right':0}

#    def draw(self):
#        frame = scale(self.video.frame, (960,740))
#
#        self.screen.blit(frame,
#            ((self.screen.get_width() - frame.get_width()) / 2,
#             (self.screen.get_height() - frame.get_height()) / 2))
