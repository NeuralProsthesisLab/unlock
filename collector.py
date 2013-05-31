from core import Screen
from apps.stimuli.ssvep import SSVEP, SSVEPStimulus
from core import UnlockApplication
from pygtec import MOBIlab
from core import viewport
from optparse import OptionParser
from os.path import join, abspath
from threading import Thread, RLock
from time import sleep

import random
import numpy as np
import time
import socket
import sys

class VisualCues(UnlockApplication):
    name = "Visual Cue"
    icon = "robot.png"  
    def __init__(self, cues_list, screen, duration, trigger, rand):
        super(self.__class__, self).__init__(screen)
        assert len(cues_list) > 0 and screen != None
        self.cues = cues_list
        self.current = 0
        self.screen = screen
        self.text = screen.drawText(self.cues[self.current], screen.width / 2,
                                    screen.height / 2)        
        self.duration = duration
        self.trial_time = 0
        self.trigger = trigger
        self.rand = rand
        self.count = 1
    def stop(self):
        self.trigger.close()    
    def update(self, dt, decision, selection):
        try:
            self.trial_time += dt
            if self.trial_time >= self.duration:
                self.trial_time = 0
                self.current = self.rand.randint(0, len(self.cues)-1) 
                self.text.text = self.cues[self.current]
                self.count += 1
                self.trigger.send(self.current+1)
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
        parser = OptionParser(version="%prog 1.3.37")
        
        msequence_help = 'adds a separate msequence pattern to each side of the screen'
        visual_cues_help = 'coma separted list of cues to display'
        duration_help = 'wall clock time between cues'
        seed_help = 'value to seed the pseudo random number generator; default value is 42'
        output_help = 'path to the output file containing the samples; defaults to gtec'
        port_help = 'sets the port to connect to to get the sample feed; default value is COM3'
        channels_help = '1 byte(2 hexidecimal digits) bit mask specifying the channels; default is 0x78'
        
        parser.add_option("-m", "--msequence", default=False, action='store_true', dest="msequence", metavar="MSEQUENCE", help=msequence_help)
        parser.add_option("-p", "--port", default='COM3', dest="port", metavar="PORT", help=port_help)
        parser.add_option("-v", "--visual-cues", default='', type=str, dest="cues", metavar="CUES", help=visual_cues_help)
        parser.add_option("-d", "--cue-duration", default=1, type=int, dest="duration", metavar="DURATION", help=duration_help)
        parser.add_option("-c", "--channels", default='0x78', dest="channels", metavar="CHANNELS", help=channels_help)
        parser.add_option("-o", "--output", default='gtec', type=str, dest="output", metavar="OUTPUT", help=output_help)
        parser.add_option("-s", "--seed", default=42, type=int, dest="seed", metavar="SEED", help=seed_help)
        
        (options, args) = parser.parse_args()
        if options.msequence == '' and options.cues == '':
            parser.print_help()
            sys.exit(1)
            
        self.duration = options.duration
        self.apps = []
        self.trigger = AsyncTrigger()
        self.rand = random.Random(options.seed)
        
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
        if options.cues != '':
            app_screen = Screen(0, 0, viewport.window.width, viewport.window.height)        
            self.vc = VisualCues(options.cues.split(','), app_screen, self.duration, self.trigger, self.rand)
            self.apps.append(self.vc)
        try:
            self.gtec = MOBIlab()
            if not self.gtec.open(options.port):
                raise Exception('MOBIlab did not open')
            if not self.gtec.init(int(options.channels, 0), 0):
                raise Exception('MOBIlab device did not initialize')
            if not self.gtec.start():
                raise Exception('DAQ device did not start streaming')
        except Exception, e:
            self.vc.stop()
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
        print "closed file"
    def stop(self):
        self.done = True
        self.vc.stop()


if __name__ == '__main__':
    s = SampleCollector()
    s.collect()

