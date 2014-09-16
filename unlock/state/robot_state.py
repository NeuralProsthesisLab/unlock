import io

from PIL import Image
import pyglet

from unlock.state import UnlockState
from unlock.util.streamclient import StreamClient


class RobotManualDriveState(UnlockState):
    def __init__(self):
        super(RobotManualDriveState, self).__init__()
        self.sc = StreamClient('128.197.61.111', 21567)
        self.frame = None

    def process_command(self, command):
        data = self.sc.get('bri/create/video.jpg')
        buffer = io.BytesIO(data)
        self.frame = pyglet.image.load('video.jpg', buffer)