import asimov
import json
import pygame
from pygame.transform import scale, scale2x
from pygame.image import save
from core import UnlockApplication

class ObjectReader(asimov.AsimovReader):
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace,
            'object/location.json', 0.5)
#        self.locations = {'1': {'x': 178, 'y': 204, 'r': 21},
#                          '2': {'x': 210, 'y': 204, 'r': 21},
#                          '3': {'x': 185, 'y': 65, 'r': 35}}
        self.frame = None
        self.objects = []


    def process(self, value):
        try:
            locations = json.loads(value)
            objects = []
            for object in locations.values():
                w = object['w']
                x = object['x'] - w/2
                if x < 0:
                    x = 0
                if x + w > 319:
                    w = 319 - x
                h = object['h']
                y = object['y'] - h/2
                if y < 0:
                    y = 0
                if y + h > 239:
                    h = 239 - y
                ob = self.frame.subsurface((x,y),(w,h))
                objects.append((ob,object))
            self.objects = objects
        except Exception as e:
            print "Object reader error: " + str(e)

class ObjectController(asimov.AsimovWriter):
    """
    Asimov interface class to set motor commands
    """
    def __init__(self, namespace):
        super(self.__class__, self).__init__(namespace)
        self.commands = None

    def process(self):
        if self.commands is not None:
            try:
                self.set('object/detect.json', self.commands)
            except Exception as e:
                pass
            self.commands = None

class RobotSelector(UnlockApplication):

    name = "Robot Selector"

    def __init__(self, screen, namespace):
        super(self.__class__, self).__init__(screen)
        self.frame = None
        self.detector = ObjectReader(namespace)
        self.writer = ObjectController(namespace)

        text = pygame.font.Font(None,72)
        self.text_waiting = text.render('Detecting...', True, (255,255,255))

        self.detector.start()
        self.writer.start()

    def onOpen(self, kwargs):
        if 'frame' in kwargs and kwargs['frame']:
            self.frame = kwargs['frame']
        else:
            raise Exception("Selection frame not set")

        self.detector.frame = self.frame
        self.detector.objects = []
        self.detector.locations = None

        self.writer.commands = '1'

    def quit(self):
        self.detector.stop()
        self.writer.commands = '-1'
        self.writer.stop()

    def update(self, decision, selection):
        if decision == 1:
            if len(self.detector.objects) >= 3:
                self.close(target=self.detector.objects[2][1])
        elif decision == 2:
            self.close()
        elif decision == 3:
            if len(self.detector.objects) >= 1:
                self.close(target=self.detector.objects[0][1])
        elif decision == 4:
            if len(self.detector.objects) >= 2:
                self.close(target=self.detector.objects[1][1])

        if selection:
            save(self.frame,"frame.jpg")

    def scale15(self,object):
        return scale(object, (int(object.get_width()*1.5), int(object.get_height()*1.5)))

    def draw(self):
        w = self.screen.get_width()
        h = self.screen.get_height()

        frame = self.scale15(self.frame)

        frame.set_alpha(64)

        self.screen.blit(frame,
            ((w - frame.get_width()) / 2,
             (h - frame.get_height()) / 2))

        if len(self.detector.objects) == 0:
            self.screen.blit(self.text_waiting,
                ((w - self.text_waiting.get_width()) / 2,
                 (h - self.text_waiting.get_height()) / 2))

        for i, obj in enumerate(self.detector.objects):
            if i > 2:
                break
            object = obj[0]
            if i == 0:
                self.screen.blit(self.scale15(object),
                    (20, (h - 1.5*object.get_height()) / 2))
            elif i == 1:
                self.screen.blit(self.scale15(object),
                    ((w - 1.5*object.get_width()) - 20,
                     (h - 1.5*object.get_height()) / 2))
            elif i == 2:
                self.screen.blit(self.scale15(object),
                    ((w - 1.5*object.get_width()) / 2, 20))

            x,y = object.get_offset()
            self.screen.blit(self.scale15(object),
                (1.5*x+((w - frame.get_width()) / 2),
                 1.5*y+(h - frame.get_height()) / 2))