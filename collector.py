from core import Screen
from core import UnlockApplication
from core import PygletWindow
from apps import SSVEP, SSVEPStimulus

try:
    from pygtec import MOBIlab
    pygtec = True
except Exception:
    pygtec = False
    
try:
    from pynobio import Enobio
    pynobio = True
except Exception:
    pynobio = False

from fakebci import FakeBCI

#if not (pynobio or pygtec):

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
    def __init__(self, window, filename, anchor_x, anchor_y, position_x, position_y):
        self.window = window
        self.filename = filename
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.position_x = position_x
        self.position_y = position_y
        self.prepare_draw()
    def prepare_draw(self):          
        self.window.clear()
        img = pyglet.image.load(self.filename).get_texture(rectangle=True)
        img.anchor_x = self.anchor_x
        img.anchor_y = self.anchor_y
        self.window.set_visible()
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
    def __init__(self, window, screen, cue_duration, indicator_duration, reset_duration, trigger, rand, trials, cue_states_factory_method_name, reset_image_filename='targets-3.png', indicator_image_filename='targets-3.png', ):
        super(self.__class__, self).__init__(screen)
        assert screen != None
        self.window = window
        self.controller = window.controller
        self.screen = screen
        self.trigger = trigger
        self.state_id = {'none': 0, 'left':1, 'right':2, 'up':3, 'down':4, 'indicator':5, 'reset':6}
        img = pyglet.image.load(reset_image_filename).get_texture(rectangle=True)
        anchor_x = img.width // 2
        anchor_y = img.height // 2
        position_x = self.window.width // 2
        position_y = self.window.height // 2


        self.text = self.screen.drawText('left', self.screen.width / 2, self.screen.height / 2)
        create_cue_states = getattr(self, cue_states_factory_method_name)
        create_cue_states(img, position_x, position_y, anchor_x, anchor_y, indicator_image_filename, cue_duration, indicator_duration, reset_duration)
        self.reset_state.next = lambda: self.cue_states[self.rand.randint(0, len(self.cues_states)-1)]
        self.state_machine = PseudoRandomTransitioner(self.cue_states, self.reset_state, rand, self.state_id, trials)
        # not sure this is correct
        self.window.event(self.state_machine)
        self.controller.draw = self.state_machine.draw
    def create_m_cue_states(self, img, position_x, postion_y, anchor_x, anchor_y, indicator_image_filename, cue_duration, indicator_duration, reset_duration):
        #self.reset_state = VisualizationState(self.state_id['reset'],
        #    ImageDraw(self.window, reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, reset_duration)
        self.reset_state = VisualizationState(self.state_id['reset'],
            TextDraw('+', self.text, self.controller.draw), self.trigger.send, reset_duration)         
        blank_indicator = VisualizationState(self.state_id['indicator'], TextDraw('', self.text, self.controller.draw), self.trigger.send, indicator_duration)
        blank_indicator.drawer.screen = self.screen
        left = CueState(self.state_id['left'], TextDraw('left', self.text, self.controller.draw), self.trigger.send, cue_duration, blank_indicator)
        right = CueState(self.state_id['right'], TextDraw('right', self.text, self.controller.draw), self.trigger.send, cue_duration, blank_indicator)
        up = CueState(self.state_id['up'], TextDraw('up', self.text, self.controller.draw), self.trigger.send, cue_duration, blank_indicator)
        down = CueState(self.state_id['down'], TextDraw('down', self.text, self.controller.draw), self.trigger.send, cue_duration, blank_indicator)
        self.cue_states = [left, right, up, down]        

    def create_emg_cue_states(self, img, position_x, position_y, anchor_x, anchor_y, indicator_image_filename, cue_duration, indicator_duration, reset_duration):
        self.reset_state = VisualizationState(self.state_id['reset'],
            ImageDraw(self.window, reset_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, reset_duration) 
        position_x = img.width // 2
        left_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        left_indicator.drawer.screen = self.screen
        
        position_x = self.window.width - img.width // 2
        right_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_x = self.window.width // 2
        position_y = self.window.height - img.height // 2
        up_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_y = img.height // 2
        down_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
    
        left = CueState(self.state_id['left'], TextDraw('left', self.text, self.controller.draw), self.trigger.send, cue_duration, left_indicator)
        right = CueState(self.state_id['right'], TextDraw('right', self.text, self.controller.draw), self.trigger.send, cue_duration, right_indicator)
        up = CueState(self.state_id['up'], TextDraw('up', self.text, self.controller.draw), self.trigger.send, cue_duration, up_indicator)
        down = CueState(self.state_id['down'], TextDraw('down', self.text, self.controller.draw), self.trigger.send, cue_duration, down_indicator)    
        self.cue_states = [left, right, up, down]

    def update(self, delta, decision, selection):
    #    print " visualation state update ", delta, decision, selection
        try:
            self.state_machine.update(UnlockState(delta, decision, selection))
        except Exception, e:
            print e
              
            
class AsyncTrigger(object):
    def __init__(self):
        #self.server = socket.socket()
        #self.server.bind(('localhost', 31337))
        #self.server.listen(1)        
        #self.server_thread = Thread(target = self.recv_thread, args = ())
        #self.server_thread.start()        
        #self.client = socket.socket()
        #self.client.connect(('localhost', 31337))    
        self.trigger = 0
        #self.lock = RLock()
    #def close(self, ):
        #self.client.close()
        #self.server_thread.join()
    def send(self, value):
        self.trigger = value #self.client.send(str(value)
        return
    ##def recv_thread(self):
    #    conn, addr = self.server.accept()
    #    while 1:
    #        data = conn.recv(1024)
    #
    #        with self.lock:
    #            if data:
    #                self.trigger = int(data)
    #            else:
    #                break
    #    conn.close()
    def value(self):
        return self.trigger
        #val = 0
        #with self.lock:
        #    val = self.trigger
        #    self.trigger = 0
        #return val
            
            
class SampleCollector(UnlockApplication):
    name = "Sample Collector"
    icon = "robot.png"  
    def __init__(self):
        super(SampleCollector, self).__init__(None)
        args = None
        options = None
        usage = "usage: %prog -m | -e [options]"
        parser = OptionParser(version="%prog 1.0", usage=usage)
        
        msequence_help = 'runs the msequence collector; one of --msequence or --emg, but not both, must be set'
        emg_help = 'runs the EMG data collector; one of --msequence or --emg, but not both, must be set'
        cue_duration_help = 'wall clock time of cue; default is 2 seconds'
        indicator_duration_help = 'wall clock time of indication; default is 3 seconds'        
        reset_duration_help = 'wall clock time of the reset; default is 1 second'
        seed_help = 'value to seed the pseudo random number generator; default value is 42'
        output_help = 'path to the output file containing the samples; defaults to gtec concatenated with the date'
        port_help = 'sets the port to connect to to get the sample feed; default value is COM3'
        channels_help = '1 byte(2 hexidecimal digits) bit mask specifying the channels; default is 0x78'
        trials_help = 'number of trials; default is 25'
        loglevel_help = 'set the logging level; valid values are debug, info, warn, error and critical; default value is warn'
        bci_help = 'selects the BCI; valid values are: fake, mobilab, enobio; default value is fake'
        parser.add_option('-m', '--msequence', default=False, action='store_true', dest='msequence', metavar='MSEQUENCE', help=msequence_help)
        parser.add_option('-p', '--port', default='COM3', dest='port', metavar='PORT', help=port_help)
        parser.add_option('-e', '--emg', default=False, action='store_true', dest='emg', metavar='emg', help=emg_help)
        parser.add_option('-d', '--cue-duration', default=2, type=int, dest='cue_duration', metavar='CUE-DURATION', help=cue_duration_help)
        parser.add_option('-i', '--indicator-duration', default=3, type=int, dest='indicator_duration', metavar='INDICATOR-DURATION', help=indicator_duration_help)        
        parser.add_option('-r', '--reset-duration', default=1, type=int, dest='reset_duration', metavar='RESET-DURATION', help=reset_duration_help)        
        parser.add_option('-c', '--channels', default='0x78', dest='channels', metavar='CHANNELS', help=channels_help)
        parser.add_option('-o', '--output', default='bci', type=str, dest='output', metavar='OUTPUT', help=output_help)
        parser.add_option('-s', '--seed', default=42, type=int, dest='seed', metavar='SEED', help=seed_help)
        parser.add_option('-t', '--trials', default=25, type=int, dest='trials', metavar='TRIALS', help=trials_help)        
        parser.add_option('-l', '--logging-level', type=str, dest='loglevel', metavar='LEVEL', help=loglevel_help)
        parser.add_option('-b', '--bci', dest='bci', default='fake', type=str, metavar='BCI', help=bci_help)        
        
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
        self.indicator_duration = options.indicator_duration
        self.reset_duration = options.reset_duration   
        self.apps = []
        self.trigger = AsyncTrigger()
        self.rand = random.Random(options.seed)
        self.cues = ['left', 'right', 'up', 'down']
        
        self.window = PygletWindow(fullscreen=True, show_fps=True)
        
        if options.msequence:
            ssvep_screen = Screen(0, 0, self.window.width, self.window.height)        
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
            cue_states_factory_method_name = 'create_m_cue_states'
            app_screen = ssvep_screen
        elif options.emg:
            app_screen = Screen(0, 0, self.window.width, self.window.height)
            cue_states_factory_method_name = 'create_emg_cue_states'
    
        self.visual_cues = VisualizationManager(self.window, app_screen, self.cue_duration, self.indicator_duration, self.reset_duration, self.trigger, self.rand, options.trials, cue_states_factory_method_name)
        self.apps.append(self.visual_cues)
        
        try:
            #self.bci = MOBIlab()
            if options.bci == 'fake' or options.bci == 'mobilab':
                if options.bci == 'fake':
                    self.bci = FakeBCI()
                else:
                    assert options.bci == 'mobilab'
                    self.bci = MOBIlab()
                self.bci_channels = 4
                if not self.bci.open(options.port):
                    raise Exception(options.bci+' did not open')
                if not self.bci.init(int(options.channels, 0), 0):
                    raise Exception(options.bci+' device did not initialize')
                if not self.bci.start():
                    raise Exception(options.bci+' device did not start streaming')                
            else:
                assert options.bci == 'enobio'
                self.bci_channels = 8
                self.bci = Enobio()
                if not self.bci.open():
                    raise Exception(options.bci+' did not open')
                #if options.bci != 'enobio' and not self.bci.init(int(options.channels, 0), 0):
                #    raise Exception(self.bci_desc+' device did not initialize')
                if not self.bci.start():
                    raise Exception(options.bci+' device did not start streaming')                

        except Exception, e:
            self.visual_cues.stop()
            raise e
        self.fh = open("%s_%d.txt" % (options.output, time.time()), 'a')
        self.done = False
    def collect(self):
        #self.thread = Thread(target = self.acquisition_loop, args = ())
        #self.thread.start()
        # XXX
        self.window.controller.set_apps([self])#self.apps)
        self.window.start()
        self.stop()
        #self.thread.join()
    def update(self, delta, decision, selection):
        for app in self.apps:
            app.update(delta, decision, selection)
        self.acquisition_loop()
    def acquisition_loop(self):
#        while not self.done:
        samples = self.bci.acquire()
        if samples == 0:
            return
        trigger_value = self.trigger.value()
        trigger_vector = np.zeros((samples, 1))
        logger.debug(trigger_vector)
        trigger_vector[-1] = trigger_value
        flat_data_vector = np.array(self.bci.getdata(self.bci_channels * samples))
#            print flat_data_vector.shape, self.bci_channels * samples
        data_matrix = flat_data_vector.reshape((samples, self.bci_channels))
        final_data_matrix = np.hstack((data_matrix, trigger_vector))
        logger.debug("Data = ", final_data_matrix)
        np.savetxt(self.fh, final_data_matrix, fmt='%d', delimiter='\t')            
    def draw(self):
        for app in self.apps:
            app.screen.batch.draw()
    def stop(self):
        self.done = True
        self.fh.flush()
        self.fh.close()
        #self.visual_cues.stop()
        
if __name__ == '__main__':
    s = SampleCollector()
    s.collect()

