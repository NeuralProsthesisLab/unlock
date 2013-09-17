import pygame
from pygame.image import load
from pygame.transform import flip, scale, scale2x
import asimov
import json
import time
import cStringIO
from core import UnlockApplication
from driver import RobotDriver
from selector import RobotSelector

class FrameGrabber(asimov.AsimovReader):
    """
    Asimov interface class to get and prepare the images streaming from the
    robot camera
    """
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace, asimov.ROBOT_VIDEO, 0.5)
        self.frame = load("resource/error.jpg")

    def process(self, value):
        try:
            buffer = cStringIO.StringIO()
            buffer.write(value)
            buffer.reset()
            self.frame = flip(load(buffer), False, True)
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


class RobotOptions(UnlockApplication):
    name = "Robot Options"

class RobotSearch(UnlockApplication):
    name = "Robot Search"


class Robot(UnlockApplication):

    name = "Robot Controller"

    def __init__(self, screen):
        super(self.__class__, self).__init__(screen)

        text = pygame.font.Font(None,36)
        self.text_drive = text.render('Driver', True, (255,255,255))
        self.text_option = text.render('Options', True, (64,64,64))
        self.text_select = text.render('Selector', True, (255,255,255))
        self.text_search = text.render('Search', True, (64,64,64))

        namespace = 'morse'
        self.video = FrameGrabber(namespace)
        self.motor = MotorController(namespace)

        self.attach(RobotDriver(screen, self.video, self.motor))
        self.attach(RobotSelector(screen, namespace))
        self.attach(RobotOptions(screen))
        self.attach(RobotSearch(screen))

        self.video.start()
        self.motor.start()

    def quit(self):
        for app in self.apps.values():
            app.quit()
        self.video.stop()
        self.motor.stop()

    def onReturn(self, kwargs):
        if 'target' in kwargs and kwargs['target']:
            target = kwargs['target']

            w = 150* (180 - target['x']) / 180.0
            now = time.time()
            program = [(now, {'left': {'w': w, 'v': 0}}),
                       (now + 0.69, {'left': {'w': 0, 'v': 0}})]
            #program = [(now, {'left': -w, 'right': w}),
            #    (now + 0.69, {'left': 0, 'right': 0})]

            self.motor.program = program


    def update(self, decision, selection):
        if decision == 1:
            self.open('Robot Driver')
        elif decision == 2:
            #self.open('Robot Options')
            pass
        elif decision == 3:
            #self.open('Robot Search')
            pass
        elif decision == 4:
            self.open('Robot Selector', frame=self.video.frame)

    def draw(self):
        w = self.screen.get_width()
        h = self.screen.get_height()

        self.screen.blit(self.text_drive,
            ((w - self.text_drive.get_width()) / 2,
            self.text_drive.get_height()))
        self.screen.blit(self.text_option,
            ((w - self.text_option.get_width()) / 2,
            h - (self.text_option.get_height() + 20)))
        self.screen.blit(self.text_select,
            (w - self.text_select.get_width() - 20,
            (h - self.text_select.get_height()) / 2))
        self.screen.blit(self.text_search,
            (20, (h - self.text_search.get_height()) / 2))

        frame = scale(self.video.frame, (int(self.video.frame.get_width()*1.5), int(self.video.frame.get_height()*1.5)))

        self.screen.blit(frame,
            ((w - frame.get_width()) / 2,
             (h - frame.get_height()) / 2))