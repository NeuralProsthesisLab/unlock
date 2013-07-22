
from unlock.model import TimedStimuli, TimedStimulus, OfflineData, RandomCueStateMachine
from unlock.view import FlickeringPygletSprite, SpritePositionComputer, PygletTextLabel, BellRingTextLabelDecorator
from unlock.util import TrialState, Trigger
from unlock.bci import FakeBCI
from controller import Canvas, UnlockController
from command import RawInlineBCIReceiver

import logging
import time
    
    
class Collector(UnlockController):
    name = "Collector"
    icon = "robot.png"  
    def __init__(self, window, views, canvas, command_receiver, cue_state, offline_data, timed_stimuli=None, standalone=True):
        super(Collector, self).__init__(window, views, canvas)
        self.command_receiver = command_receiver
        self.cue_state = cue_state
        self.offline_data = offline_data
        self.timed_stimuli = timed_stimuli
        self.standalone = standalone
        self.logger = logging.getLogger(__name__)
        
    def poll_bci(self, delta):
        
        self.logger.debug('Collector.poll bci delta = ', delta, ' time = ', time.time())
        command = self.command_receiver.next_command(delta)
        if self.timed_stimuli:
            sequence_trigger = self.timed_stimuli.process_command(command)
            if sequence_trigger != Trigger.Null:
                command.set_sequence_trigger(sequence_trigger)
                
        cue_trigger = self.cue_state.process_command(command)
        command.set_cue_trigger(cue_trigger)
            
        command.matrixize()
        self.offline_data.process_command(command)
        
    def activate(self):
        self.cue_state.start()
        self.timed_stimuli.start()
        self.offline_data.start()
        super(Collector, self).activate()
        
    def quit(self):
        self.command_receiver.stop()
        self.timed_stimuli.stop()
        self.cue_state.stop()
        self.offline_data.stop()
        self.window.deactivate_controller()
        return self.standalone
    
    @staticmethod
    def create(mode, port, cue_duration, indicate_duration, rest_duration, channels, trials, seed, output):        
        pass
        
    @staticmethod
    def create_emg_collector():
        pass
        
    @staticmethod
    def create_msequence_collector(window, bci=FakeBCI(), stimulation_duration=4.0, trials=25, cue_duration=1, rest_duration=2, indicate_duration=4, output_file='bci', seed=42):
        
        canvas = Canvas.create(window.width, window.height)
        
        timed_stimuli = TimedStimuli.create(stimulation_duration)
        
        north_stimulus = TimedStimulus.create(15.0,  sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0))
        fs = FlickeringPygletSprite.create_flickering_checkered_box_sprite(north_stimulus, canvas, SpritePositionComputer.North, width=200, height=200, xfreq=4, yfreq=4)
        timed_stimuli.add_stimulus(north_stimulus)
        
        east_stimulus = TimedStimulus.create(15.0, sequence=(0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0))
        fs1 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(east_stimulus, canvas, SpritePositionComputer.East, 90, width=200, height=200, xfreq=4, yfreq=4)
        timed_stimuli.add_stimulus(east_stimulus)
        
        south_stimulus = TimedStimulus.create(15.0, sequence=(0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1))
        fs2 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(south_stimulus, canvas, SpritePositionComputer.South, width=200, height=200, xfreq=4, yfreq=4)
        timed_stimuli.add_stimulus(south_stimulus)
        
        west_stimulus = TimedStimulus.create(15.0, sequence=(0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0))
        fs3 = FlickeringPygletSprite.create_flickering_checkered_box_sprite(west_stimulus, canvas, SpritePositionComputer.West, 90, width=200, height=200, xfreq=4, yfreq=4)
        timed_stimuli.add_stimulus(west_stimulus)

        cue_state = RandomCueStateMachine.create(25, [Trigger.Up, Trigger.Right, Trigger.Down, Trigger.Left], cue_duration, rest_duration, indicate_duration, seed=seed)
        
        up = PygletTextLabel(cue_state.cue_states[0], canvas, 'up', canvas.width / 2.0, canvas.height / 2.0)
        right = PygletTextLabel(cue_state.cue_states[1], canvas, 'right', canvas.width / 2.0, canvas.height / 2.0)
        down = PygletTextLabel(cue_state.cue_states[2], canvas, 'down', canvas.width / 2.0, canvas.height / 2.0)
        left = PygletTextLabel(cue_state.cue_states[3], canvas, 'left', canvas.width / 2.0, canvas.height / 2.0)
        
        rest_text = PygletTextLabel(cue_state.rest_state, canvas, '+', canvas.width / 2.0, canvas.height / 2.0)
        rest = BellRingTextLabelDecorator(rest_text)        
        
        indicate_text = PygletTextLabel(cue_state.indicate_state, canvas, '', canvas.width / 2.0, canvas.height / 2.0)
        indicate = BellRingTextLabelDecorator(indicate_text)
        
        command_receiver = RawInlineBCIReceiver(bci)
        
        offline_data = OfflineData(output_file)
        
        return Collector(window, [fs, fs1, fs2, fs3, up, right, down, left, rest, indicate], canvas, command_receiver, cue_state, offline_data, timed_stimuli)
        
##        controller.make_active()
# #       window.switch_to()
#        self.mode = None
#        self.port = None
#        self.cue_duration = 1
#        self.indicator_duration = 2
#        self.reset_duration = 1
#        self.channels = 0x78
#        self.trials = 25
#        self.seed = 42
#        self.output = 'bci'
#        self.rand = random.Random(self.seed)
#        self.cues = ['left', 'right', 'up', 'down']
#        self.start_sequence_trigger = None
#        self.window = window#PygletWindow(fullscreen=options.not_fullscreen, show_fps=options.fps)
#                # xxx??
#
#        self.fh.flush()
#        self.fh.close()
        
        
