from unlock.model import TimedStimulus, HierarchyGridState, TimedStimuli
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, HierarchyGridView
from unlock.decoders import HarmonicSumDecision
from unlock.controller import UnlockController, Canvas, RawInlineSignalReceiver
import inspect
import os


class VEP(UnlockController):
    def __init__(self, window, views, canvas, command_receiver, timed_stimuli,
                 grid_state, decoder, icon="LazerToggleS.png", name="VEP"):
        super(VEP, self).__init__(window, views, canvas)
        self.command_receiver = command_receiver
        self.timed_stimuli = timed_stimuli
        self.grid_state = grid_state
        self.decoder = decoder
        self.name = name
        self.icon = icon
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(VEP)),
                                      'resource', self.icon)

    def __handle_command__(self, command):
        self.grid_state.process_command(command)

    def keyboard_input(self, command):
        self.__handle_command__(command)

    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        self.timed_stimuli.process_command(command)
        # for s in self.timed_stimuli:
        #     s.process_command(command)
        if command.raw_data_vector.size > 0:
            command.make_matrix()
            self.decoder.process_command(command)
        self.__handle_command__(command)
        self.render()
        
    def activate(self):
        self.timed_stimuli.start()
        # for s in self.timed_stimuli:
        #     s.start()
        super(VEP, self).activate()
        
    def deactivate(self):
        self.command_receiver.stop()
        self.timed_stimuli.stop()
        # for s in self.timed_stimuli:
        #     s.stop()
        self.window.deactivate_controller()
        return False
        
    @staticmethod
    def create_ssvep(window, signal, timer, color='bw'):
        canvas = Canvas.create(window.width, window.height)

        if color == 'bw':
            color1 = (255, 0, 0)
            color2 = (255, 255, 0)
        else:
            color1 = (0, 0, 0)
            color2 = (255, 255, 255)

        stimuli = TimedStimuli.create(4.0)
        views = []

        freqs = [12.0, 13.0, 14.0, 15.0]

        stimulus1 = TimedStimulus.create(freqs[0] * 2)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=500,
            height=100, xfreq=5, yfreq=1, color_on=color1, color_off=color2,
            reversal=False)
        #stimuli.append(stimulus1)
        stimuli.add_stimulus(stimulus1)
        views.append(fs1)

        stimulus2 = TimedStimulus.create(freqs[1] * 2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=500,
            height=100, xfreq=5, yfreq=1, color_on=color1, color_off=color2,
            reversal=False)
        #stimuli.append(stimulus2)
        stimuli.add_stimulus(stimulus2)
        views.append(fs2)

        stimulus3 = TimedStimulus.create(freqs[2] * 2)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=100,
            height=500, xfreq=1, yfreq=5, color_on=color1, color_off=color2,
            xoffset=250, reversal=False)
        #stimuli.append(stimulus3)
        stimuli.add_stimulus(stimulus3)
        views.append(fs3)

        stimulus4 = TimedStimulus.create(freqs[3] * 2)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=100,
            height=500, xfreq=1, yfreq=5, color_on=color1, color_off=color2,
            xoffset=-250, reversal=False)
        #stimuli.append(stimulus4)
        stimuli.add_stimulus(stimulus4)
        views.append(fs4)

        grid_model = HierarchyGridState(2)
        grid = HierarchyGridView(grid_model, canvas)
        views.append(grid)

        decoder = HarmonicSumDecision(freqs, 3.0, 500, 8)

        command_receiver = RawInlineSignalReceiver(signal, timer)
        return VEP(window, views, canvas, command_receiver, stimuli,
                   grid_model, decoder, name='SSVEP')

    @staticmethod
    def create_msequence(window, signal, timer, color='bw'):
        canvas = Canvas.create(window.width, window.height)

        rate = 30.0
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

        seq1 = (1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,0,1,1)
        seq2 = (0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1)
        seq3 = (0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0)
        seq4 = (0,1,0,1,1,1,1,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1,1,0,1,0,0,1,1,0)

        stimuli = []
        views = []

        stimulus1 = TimedStimulus.create(rate, sequence=seq1)
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus1, canvas, SpritePositionComputer.North, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.append(stimulus1)
        views.append(fs1)

        stimulus2 = TimedStimulus.create(rate, sequence=seq2)
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus2, canvas, SpritePositionComputer.South, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.append(stimulus2)
        views.append(fs2)

        stimulus3 = TimedStimulus.create(rate, sequence=seq3)
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus3, canvas, SpritePositionComputer.West, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.append(stimulus3)
        views.append(fs3)

        stimulus4 = TimedStimulus.create(rate, sequence=seq4)
        fs4 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(
            stimulus4, canvas, SpritePositionComputer.East, width=width,
            height=height, xfreq=fx, yfreq=fy, color_on=color1,
            color_off=color2)
        stimuli.append(stimulus4)
        views.append(fs4)

        command_receiver = RawInlineSignalReceiver(signal, timer)
        return VEP(window, views, canvas, command_receiver, stimuli, None,
                   None, "emg-100x100.jpg", name='cVEP')