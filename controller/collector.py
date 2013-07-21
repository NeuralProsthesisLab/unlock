
#from unlock.core import Screen
#from unlock.core import UnlockApplication
#from unlock.core import PygletWindow
#from unlock.apps import SSVEP, SSVEPStimulus

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

from bci import FakeBCI

#if not (pynobio or pygtec):

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
import os
import inspect


            
class VisualizationManager(UnlockApplication):
    def __init__(self, window, screen, cue_duration, indicator_duration, reset_duration, trigger, rand, trials, cue_states_factory_method_name, reset_image_filename=path+'/targets-3.png', indicator_image_filename=path+'/targets-3.png', ):
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

    def create_emg_cue_states(self, img, position_x, position_y, anchor_x, anchor_y, reset_indicator_image_filename, cue_duration, indicator_duration, reset_duration):
        self.reset_state = VisualizationState(self.state_id['reset'],
            ImageDraw(self.window, reset_indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, reset_duration) 
        position_x = img.width // 2
        left_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, reset_indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        left_indicator.drawer.screen = self.screen
        
        position_x = self.window.width - img.width // 2
        right_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, reset_indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_x = self.window.width // 2
        position_y = self.window.height - img.height // 2
        up_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, reset_indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
        
        position_y = img.height // 2
        down_indicator = VisualizationState(self.state_id['indicator'],
            ImageDraw(self.window, reset_indicator_image_filename, anchor_x, anchor_y, position_x, position_y), self.trigger.send, indicator_duration)
    
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
              
            

        
class Collector(UnlockController):
    name = "Collector"
    icon = "robot.png"  
    def __init__(self, trigger, window, app_screen, timed_stimuli):
        super(Collector, self).__init__(None)
        self.trigger = trigger
        self.mode = None
        self.port = None
        self.cue_duration = 1
        self.indicator_duration = 2
        self.reset_duration = 1
        self.channels = 0x78
        self.trials = 25
        self.seed = 42
        self.output = 'bci'
        self.rand = random.Random(self.seed)
        self.cues = ['left', 'right', 'up', 'down']
        self.start_sequence_trigger = None
        self.window = window#PygletWindow(fullscreen=options.not_fullscreen, show_fps=options.fps)
        self.timed_stimuli = timed_stimuli
        
    def start(self):
        if mode == msequence:
            cue_states_factory_method_name = 'create_m_cue_states'
        else:
           cue_states_factory_method_name = 'create_emg_cue_states'
           
#       elif options.emg:
#          app_screen = Screen(0, 0, self.window.width, self.window.height)

    
        self.visual_cues = VisualizationManager(self.window, app_screen, self.cue_duration, self.indicator_duration, self.reset_duration, self.trigger, self.rand, self.trials, cue_states_factory_method_name)
        self.apps.append(self.visual_cues)
   
   
   
        self.fh = open("%s_%d.txt" % (options.output, time.time()), 'a')
        self.done = False
        
        self.window.controller.set_apps([self])#self.apps)
        self.window.start()
        
        self.done = True
        self.fh.flush()
        self.fh.close()
        
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
        trigger_vector[-1] = trigger_value
        logger.debug(trigger_vector)
        if self.start_sequence_trigger != None:
            sequence_start_value = self.start_sequence_trigger.value()
            sequence_start_vector = np.zeros((samples, 1))
            sequence_start_vector[-1] = sequence_start_value

        flat_data_vector = np.array(self.bci.getdata(self.bci_channels * samples))
#            print flat_data_vector.shape, self.bci_channels * samples
        data_matrix = flat_data_vector.reshape((samples, self.bci_channels))
        #final_data_matrix = np.hstack((data_matrix, trigger_vector))#, sequence_start_vector))
        if self.start_sequence_trigger != None:
            final_data_matrix = np.hstack((data_matrix, trigger_vector, sequence_start_vector))
        else:
            final_data_matrix = np.hstack((data_matrix, trigger_vector))#, sequence_start_vector))
        #print final_data_matrix
        logger.debug("Data = ", final_data_matrix)
        np.savetxt(self.fh, final_data_matrix, fmt='%d', delimiter='\t')
        #np.savetxt(self.fh, final_data_matrix1, fmt='%d', delimiter='\t')            
    def draw(self):
        for app in self.apps:
            app.screen.batch.draw()
        
#if __name__ == '__main__':
#    s = SampleCollector()
#    s.collect()

