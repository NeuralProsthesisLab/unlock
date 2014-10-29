import io
import json

import pyglet

from unlock.state import UnlockState
from unlock.util.streamclient import StreamClient


class RobotManualDriveState(UnlockState):
    SERVO_SPEED = 0.175
    WHEEL_SPEED = 100

    def __init__(self):
        super(RobotManualDriveState, self).__init__()
        self.sc = StreamClient('128.197.61.111', 21567)
        self.frame = None
        self.ready = True

    def process_command(self, command):
        cmds = {}
        if command.decision == 1:
            cmds['wheels'] = [self.WHEEL_SPEED, self.WHEEL_SPEED]
        elif command.decision == 2:
            cmds['wheels'] = [-self.WHEEL_SPEED, -self.WHEEL_SPEED]
        elif command.decision == 3:
            cmds['wheels'] = [self.WHEEL_SPEED/2, -self.WHEEL_SPEED/2]
        elif command.decision == 4:
            cmds['wheels'] = [-self.WHEEL_SPEED/2, self.WHEEL_SPEED/2]

        if command.selection:
            cmds['wheels'] = [0, 0]

        if len(cmds) > 0:
            self.sc.set('bri/command', json.dumps(cmds))

        if self.ready:
            try:
                data = self.sc.get('bri/create/video.jpg')
                buffer = io.BytesIO(data)
                self.frame = pyglet.image.load('video.jpg', buffer)
            except:
                pass
        self.ready = not self.ready
