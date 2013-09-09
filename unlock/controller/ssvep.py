
from unlock.model import TimedStimulus, TimedStimuli
from unlock.view import FlickeringPygletSprite, SpritePositionComputer
from .controller import UnlockController, Canvas
from .command import DeltaCommandReceiver, RawInlineSignalReceiver
import inspect
import os

class SSVEP(UnlockController):
    def __init__(self, window, views, canvas, command_receiver, timed_stimuli, icon="LazerToggleS.png", name="SSVEP"):
        super(SSVEP, self).__init__(window, views, canvas)
        self.command_receiver = command_receiver
        self.timed_stimuli = timed_stimuli
        self.name = name
        self.icon = icon
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(SSVEP)), 'resource', self.icon)        

    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        for s in self.timed_stimuli:
            s.process_command(command)

        self.render()
        
    def activate(self):
        for s in self.timed_stimuli:
            s.start()
        super(SSVEP, self).activate()
        
    def deactivate(self):
        self.command_receiver.stop()
        for s in self.timed_stimuli:
            s.stop()
        self.window.deactivate_controller()
        return False
        
    @staticmethod
    def create_ssvep(window, signal):
        canvas = Canvas.create(window.width, window.height)

        color1 = (255, 0, 0)
        color2 = (255, 255, 0)

        stimulus1 = TimedStimulus.create(12.0)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=600,
            height=100, xfreq=6, yfreq=1, color_on=color1, color_off=color2,
            reversal=False)
        stimulus2 = TimedStimulus.create(13.0)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=600,
            height=100, xfreq=6, yfreq=1, color_on=color1, color_off=color2,
            reversal=False)
        stimulus3 = TimedStimulus.create(14.0)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=100,
            height=600, xfreq=1, yfreq=6, color_on=color1, color_off=color2,
            reversal=False)
        stimulus4 = TimedStimulus.create(15.0)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=100,
            height=600, xfreq=1, yfreq=6, color_on=color1, color_off=color2,
            reversal=False)
        stimuli = [stimulus1, stimulus2, stimulus3, stimulus4]
#        command_receiver = DeltaCommandReceiver()
        command_receiver = RawInlineSignalReceiver(signal)
        return SSVEP(window, [fs1, fs2, fs3, fs4], canvas, command_receiver,
                     stimuli)

    @staticmethod
    def create_msequence(window, signal, color='bw'):
        canvas = Canvas.create(window.width, window.height)

        fd = 15.0
        width = 300
        height = 300
        fx = 4
        fy = 4

        if color == 'ry':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (255, 255, 255)
            color2 = (0, 0, 0)

        seq1 = (1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0)
        seq2 = (0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0)
        seq3 = (0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1)
        seq4 = (0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0)

        stimulus1 = TimedStimulus.create(fd, sequence=seq1)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1, color_off=color2)

        stimulus2 = TimedStimulus.create(fd, sequence=seq2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1, color_off=color2)

        stimulus3 = TimedStimulus.create(fd, sequence=seq3)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1, color_off=color2)

        stimulus4 = TimedStimulus.create(fd, sequence=seq4)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1, color_off=color2)

        stimuli = [stimulus1, stimulus2, stimulus3, stimulus4]
#        command_receiver = DeltaCommandReceiver()
        command_receiver = RawInlineSignalReceiver(signal)
        return SSVEP(window, [fs1, fs2, fs3, fs4], canvas, command_receiver,
                         stimuli, "emg-100x100.jpg")