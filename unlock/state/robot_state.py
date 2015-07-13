import io
import json

import pyglet

from unlock.state import UnlockState
from unlock.util.streamclient import StreamClient


class RobotManualDriveState(UnlockState):
    SERVO_SPEED = 0.175
    WHEEL_SPEED = 50

    def __init__(self, manual):
        super(RobotManualDriveState, self).__init__()
        self.manual = manual
        self.sc = StreamClient('128.197.61.111', 21567)
        self.frame = None
        self.goals = ('green', 'blue', 'red2')
        self.goal = None

    def process_command(self, command):
        if self.manual:
            self.process_manual_command(command)
        else:
            self.process_auto_command(command)

        try:
            data = self.sc.get('bri/create/video.jpg')
            buffer = io.BytesIO(data)
            self.frame = pyglet.image.load('video.jpg', buffer)
        except:
            pass

    def process_manual_command(self, command):
        cmds = {}
        if command.decision == 1:
            cmds['wheels'] = [self.WHEEL_SPEED, self.WHEEL_SPEED]
        elif command.decision == 2:
            cmds['wheels'] = [-self.WHEEL_SPEED, -self.WHEEL_SPEED]
        elif command.decision == 3:
            cmds['wheels'] = [self.WHEEL_SPEED, -self.WHEEL_SPEED]
        elif command.decision == 4:
            cmds['wheels'] = [-self.WHEEL_SPEED, self.WHEEL_SPEED]

        if command.selection:
            cmds['wheels'] = [0, 0]

        if len(cmds) > 0:
            self.sc.set('bri/command', json.dumps(cmds))

    def process_auto_command(self, command):
        change = False
        if self.goal is None:
            if command.decision == 1:
                # self.goal = self.goals[1]
                # change = True
                pass
            elif command.decision == 2:
                pass
            elif command.decision == 3:
                self.goal = self.goals[0]
                change = True
            elif command.decision == 4:
                self.goal = self.goals[2]
                change = True

        if command.selection:
            self.goal = None
            change = True

        if change:
            cmds = {'goal': self.goal}
            if self.goal is None:
                cmds['wheels'] = [0, 0]
            self.sc.set('bri/command', json.dumps(cmds))
