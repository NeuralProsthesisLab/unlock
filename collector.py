from core import Screen
from apps.stimuli.ssvep import SSVEP, SSVEPStimulus
from core import UnlockApplication
from pygtec import MOBIlab
from core import viewport
from optparse import OptionParser
from os.path import join, abspath
from threading import Thread, RLock
from time import sleep
from pyglet.gl import *

import pyglet
import random
import numpy as np
import time
import socket
import sys

import logging
import logging.config
try:
    logging.config.fileConfig('logger.config')
except:
    pass
#logging.config.string

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
                    
def set_logger_level(log_level):
    logger.setLevel(log_level)

  
class UnlockState(object):
    def __init__(self, delta, decision, selection):
        self.delta = delta
        self.decision = decision
        self.selection = selection
    def display(self):
        logger.debug( 'delta = ', self.delta, ' decision = ', self.decision, ' selection = ', self.selection)
        
      
class TextDraw(object):
    def __init__(self, cue, text, controller_draw):
        self.cue = cue
        self.text = text
        self.controller_draw = controller_draw
    def prepare_draw(self):
        self.text.text = self.cue
    def draw(self):
        self.controller_draw()
        
        
class ImageDraw(object):
    def __init__(self, filename, anchor_x, anchor_y, position_x, position_y):
        self.filename = filename
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.position_x = position_x
        self.position_y = position_y
        self.prepare_draw()
    def prepare_draw(self):          
        viewport.window.clear()
        img = pyglet.image.load(self.filename).get_texture(rectangle=True)
        img.anchor_x = self.anchor_x
        img.anchor_y = self.anchor_y
        viewport.window.set_visible()
        self.img = img
    def draw(self):
        self.img.blit(self.position_x, self.position_y, 0)
        
        
class VisualizationState(object):
    def __init__(self, state_id, drawer, draw_notifier, duration):
        self.state_id = state_id
        self.drawer = drawer
        self.draw_notifier = draw_notifier
        self.duration = duration
        self.trial_time = 0
        self.count = 0 
    def draw(self):
        self.drawer.draw()
    def update(self, unlock_state):
        if self.trial_time == 0:
            self.drawer.prepare_draw()            
            self.draw_notifier(self.state_id)
        self.trial_time += unlock_state.delta
        if self.trial_time >= self.duration:
            self.trial_time = 0
            return True
        else:
            return False                    

class CueState(VisualizationState):
    def __init__(self, state_id, drawer, draw_notifier, duration, indicator):
        super(self.__class__, self).__init__(state_id, drawer, draw_notifier, duration)
        self.indicator = indicator

class PseudoRandomTransitioner(object):
    def __init__(self, cue_states, reset_state, rand, state_id, trials):
        self.cue_states = cue_states
        self.reset_state = reset_state
        self.state = reset_state
        self.rand = rand
        self.state_id = state_id
        self.trials = trials
        self.count = 0
        self.transition = False
    def update(self, unlock_state):
        unlock_state.display()
        if self.transition:
            self.state = self.next_state()
        self.transition = self.state.update(unlock_state)

    def next_state(self):
        if self.state.state_id == self.state_id['reset']:
            state = self.next_cue()
        elif self.state.state_id == self.state_id['indicator']:
            state = self.reset_state
            self.count += 1
            if self.count > self.trials:
                pyglet.app.exit()
        elif self.state.state_id < self.state_id['indicator']:
            assert self.state.state_id > self.state_id['none']
            state = self.state.indicator
        return state
    def next_cue(self):
        return self.cue_states[self.rand.randint(0, len(self.cue_states)-1)]
    def draw(self):
        self.state.draw()
            
            
class VisualizationManager(UnlockApplication):
    def __init__(self, screen, indicator_duration, cue_duration, reset_duration, trigger, rand, trials, reset_image_filename='targets.jpg'):
        super(self.__class__, self).__init__(screen)
        assert screen != None
        self.screen = screen
        self.trigger = trigger
        self.state_id = {'none': 0, 'left':1, 'right':2, 'up':3, 'down':4, 'indicator':5, 'reset':6}
        img = pyglet.image.load(reset_image_filename).get_texture(rectangle=True)
        anchor_x = img.width // 2
        anchor_y = img.height // 2
        position_x = viewport.window.width // 2
        position_y = viewport.window.height // 2
        self.reset_state = VisualizationState(self.state_id['reset'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, reset_duration)
 
        self.text = self.screen.drawText('left', self.screen.width / 2, self.screen.height / 2)
#        self.reset_state = CueState(self.state_id['reset'], TextDraw('+', self.text, viewport.controller.draw), self.trigger.send, reset_duration, None)

        position_x = img.width // 2
        self.left_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        self.left_indicator.drawer.screen = screen
        
        position_x = viewport.window.width - img.width // 2
        self.right_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_x = viewport.window.width // 2
        position_y = viewport.window.height - img.height // 2
        self.up_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_y = img.height // 2
        self.down_indicator = VisualizationState(self.state_id['indicator'], ImageDraw(reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)

        self.left = CueState(self.state_id['left'], TextDraw('left', self.text, viewport.controller.draw), self.trigger.send, cue_duration, self.left_indicator)
        self.right = CueState(self.state_id['right'], TextDraw('right', self.text, viewport.controller.draw), self.trigger.send, cue_duration, self.right_indicator)
        self.up = CueState(self.state_id['up'], TextDraw('up', self.text, viewport.controller.draw), self.trigger.send, cue_duration, self.up_indicator)
        self.down = CueState(self.state_id['down'], TextDraw('down', self.text, viewport.controller.draw), self.trigger.send, cue_duration, self.down_indicator)

        self.cue_states = [self.left, self.right, self.up, self.down]
        self.reset_state.next = lambda: self.cue_states[self.rand.randint(0, len(self.cues_states)-1)]
        
        self.state_machine = PseudoRandomTransitioner(self.cue_states, self.reset_state, rand, self.state_id, trials)        
        viewport.window.event(self.state_machine)
        viewport.controller.draw = self.state_machine.draw
    def stop(self):
        self.trigger.close()
    def update(self, delta, decision, selection):
        try:
            self.state_machine.update(UnlockState(delta, decision, selection))
        except Exception, e:
            print e
              
            
class AsyncTrigger(object):
    def __init__(self):
        self.server = socket.socket()
        self.server.bind(('localhost', 31337))
        self.server.listen(1)        
        self.server_thread = Thread(target = self.recv_thread, args = ())
        self.server_thread.start()        
        self.client = socket.socket()
        self.client.connect(('localhost', 31337))    
        self.trigger = 0
        self.lock = RLock()
    def close(self, ):
        self.client.close()
        self.server_thread.join()
    def send(self, value):
        self.client.send(str(value))
    def recv_thread(self):
        conn, addr = self.server.accept()
        while 1:
            data = conn.recv(1024)

            with self.lock:
                if data:
                    self.trigger = int(data)
                else:
                    break
        conn.close()
    def value(self):
        val = 0
        with self.lock:
            val = self.trigger
            self.trigger = 0
        return val
            
            
class SampleCollector(UnlockApplication):
    name = "Sample Collector"
    icon = "robot.png"  
    def __init__(self):
        args = None
        options = None
        usage = "usage: %prog -m | -e [options]"
        parser = OptionParser(version="%prog 1.0", usage=usage)
        
        msequence_help = 'runs the msequence collector; one of --msequence or --emg, but not both, must be set'
        emg_help = 'runs the EMG data collector; one of --msequence or --emg, but not both, must be set'
        cue_duration_help = 'wall clock time between cues; default is 3 seconds'
        reset_duration_help = 'wall clock time of the reset; default is 1 second'
        seed_help = 'value to seed the pseudo random number generator; default value is 42'
        output_help = 'path to the output file containing the samples; defaults to gtec concatenated with the date'
        port_help = 'sets the port to connect to to get the sample feed; default value is COM3'
        channels_help = '1 byte(2 hexidecimal digits) bit mask specifying the channels; default is 0x78'
        trials_help = 'number of trials; default is 25'
        loglevel_help = 'set the logging level; valid values are debug, info, warn, error and critical; default value is warn'
        parser.add_option('-m', '--msequence', default=False, action='store_true', dest='msequence', metavar='MSEQUENCE', help=msequence_help)
        parser.add_option('-p', '--port', default='COM3', dest='port', metavar='PORT', help=port_help)
        parser.add_option('-e', '--emg', default=False, action='store_true', dest='emg', metavar='emg', help=emg_help)
        parser.add_option('-d', '--cue-duration', default=3, type=int, dest='cue_duration', metavar='CUE-DURATION', help=cue_duration_help)
        parser.add_option('-r', '--reset-duration', default=1, type=int, dest='reset_duration', metavar='RESET-DURATION', help=reset_duration_help)        
        parser.add_option('-c', '--channels', default='0x78', dest='channels', metavar='CHANNELS', help=channels_help)
        parser.add_option('-o', '--output', default='gtec', type=str, dest='output', metavar='OUTPUT', help=output_help)
        parser.add_option('-s', '--seed', default=42, type=int, dest='seed', metavar='SEED', help=seed_help)
        parser.add_option('-t', '--trials', default=25, type=int, dest='trials', metavar='TRIALS', help=trials_help)        
        parser.add_option('-l', '--logging-level', dest='loglevel', metavar='LEVEL', help=loglevel_help)
        
        valid_levels = { 'debug' : logging.DEBUG, 'info' : logging.INFO,
                         'warn' : logging.WARN, 'error' : logging.ERROR,
                         'critical' : logging.CRITICAL} 
        
        (options, args) = parser.parse_args()
        if (options.msequence == False and options.emg == False) or (options.msequence == True and options.emg == True):
            parser.print_help()
            sys.exit(1)
    
        if options.loglevel != None and options.loglevel in valid_levels:
            set_logger_level(valid_levels[options.loglevel])
        else:
            if options.loglevel:
                logger.error('Invalid log level: '+self.options.loglevel+ \
                             ' using default, which is WARN')
            set_logger_level(logging.WARN)
    
        self.cue_duration = options.cue_duration
        self.reset_duration = options.reset_duration        
        self.apps = []
        self.trigger = AsyncTrigger()
        self.rand = random.Random(options.seed)
        self.cues = ['left', 'right', 'up', 'down']
        
        if options.msequence:
            ssvep_screen = Screen(0, 0, viewport.window.width, viewport.window.height)        
            stimuli = [
                SSVEPStimulus(ssvep_screen, 15.0, 'north', width=200, height=200,
                    x_freq=4, y_freq=4, filename_reverse=True,
                    sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0)),
                SSVEPStimulus(ssvep_screen, 15.0, 'south', width=200, height=200,
                    x_freq=4, y_freq=4, filename_reverse=True,
                    sequence=(0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1)),
                        
                SSVEPStimulus(ssvep_screen, 15.0, 'east', width=200, height=200,
                    x_freq=4, y_freq=4, filename_reverse=True,
                    sequence=(0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0)),
                SSVEPStimulus(ssvep_screen, 15.0, 'west', width=200, height=200,
                    x_freq=4, y_freq=4, filename_reverse=True,
                    sequence=(0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0))
            ]
            ssvep = SSVEP(ssvep_screen, stimuli, rest_length=0)
            # Uncomment the following line to turn off the flickering stimuli.
            #ssvep.stop()
            self.apps.append(ssvep)
        
        app_screen = Screen(0, 0, viewport.window.width, viewport.window.height)        
        self.visual_cues = VisualizationManager(app_screen, self.cue_duration, self.reset_duration, self.reset_duration, self.trigger, self.rand, options.trials)
        self.apps.append(self.visual_cues)
        
        try:
            self.gtec = MOBIlab()
            if not self.gtec.open(options.port):
                raise Exception('MOBIlab did not open')
            if not self.gtec.init(int(options.channels, 0), 0):
                raise Exception('MOBIlab device did not initialize')
            if not self.gtec.start():
                raise Exception('DAQ device did not start streaming')
        except Exception, e:
            self.visual_cues.stop()
            raise e
        self.fh = open("%s_%d.txt" % (options.output, time.time()), 'a')
        self.done = False
    def collect(self):
        self.thread = Thread(target = self.acquisition_loop, args = ())
        self.thread.start()
        viewport.controller.set_apps(self.apps)
        viewport.start()
        self.stop()
        self.thread.join()
    def acquisition_loop(self):
        while self.gtec.acquire() and not self.done:
            tval = self.trigger.value()
            data = np.hstack((self.gtec.getdata(4), [tval]))
            data = data.reshape((1, 5))
            np.savetxt(self.fh, data, fmt='%d', delimiter='\t')            
        self.fh.flush()
        self.fh.close()
    def stop(self):
        self.done = True
        self.visual_cues.stop()
        
if __name__ == '__main__':
    s = SampleCollector()
    s.collect()

