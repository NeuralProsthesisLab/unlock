# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import json
import traceback
import inspect

import logging
import logging.config

from unlock import context
from unlock.decode import CommandReceiverFactory
from unlock.controller import PygletWindow, Dashboard, FastPad, Canvas, Calibrate, GridSpeak, Collector
from optparse import OptionParser


class UnlockFactory(context.PythonConfig):
    def __init__(self, args):
        super(UnlockFactory, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.args = args
        self.mac_addr = None
        self.window = None
        self.calibrator = None
        self.stimuli = None
        if 'receiver' in self.args.keys():
            self.receiver = CommandReceiverFactory.map_factory_method(self.args['receiver'])
        else:
            self.receiver = CommandReceiverFactory.Classified
            
        if 'mac_addr' in self.args.keys():
            self.mac_addr = [int(value,0) for value in [x.strip() for x in self.args['mac_addr'].split(',')]]
            
            
    @context.Object(lazy_init=True)        
    def ssvep(self):
        from unlock.controller import EEGControllerFragment
        canvas = Canvas.create(self.window.width, self.window.height)
        stimuli = EEGControllerFragment.create_ssvep(canvas, self.signal, self.timer, receiver_type=self.receiver)
        return stimuli
        
    @context.Object(lazy_init=True)        
    def semg(self):
        from unlock.controller import sEMGControllerFragment
        stimuli = sEMGControllerFragment.create_semg(self.signal, self.timer, receiver_type=self.receiver)
        return stimuli
        
    @context.Object(lazy_init=True)        
    def audio(self):
        from unlock.decode import acquire
        self.timer = acquire.create_timer()
        signal = acquire.AudioSignal()
        
        if not signal.start():
            raise RuntimeError('failed to start audio signal')
            
        return signal        
        
    @context.Object(lazy_init=True)    
    def enobio(self):
        from unlock.decode import acquire
        if self.mac_addr == None:
            print ('enobio requires a mac address; none set')
            raise RuntimeError('enobio requires a mac address; none set')
            
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_enobio_signal(self.timer)
        if not signal.open(self.mac_addr):
            print('enobio did not open')
            raise RuntimeError('enobio did not open')
        if not signal.start():
            print('enobio device did not start streaming')                                 
            raise RuntimeError('enobio device did not start streaming')                       
        return signal
        
    @context.Object(lazy_init=True)    
    def mobilab(self, comport='COM5', analog_channels_bitmask=120):
        from unlock.decode import acquire
        
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_mobilab_signal(self.timer, analog_channels_bitmask, 0, comport)
        
        if not signal.start():
            print('mobilab device did not start streaming') 
            raise RuntimeError('mobilab device did not start streaming')                       
        return signal
    
    @context.Object(lazy_init=True)
    def random(self):
        from unlock.decode import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_random_signal(self.timer)
        signal.open([])
        signal.start()
        return signal
        
    @context.Object(lazy_init=True)
    def PygletWindow(self):
        return PygletWindow(self.signal, self.args['fullscreen'], self.args['fps'], self.args['vsync'])        
        
    @context.Object(lazy_init=True)
    def CalibrateSEMG(self):
        self.calibrator, calibrator = Calibrate.create_smg_calibrator(self.window, self.signal,
                                                                      self.timer, self.stimuli,
                                                                      receiver_type=self.receiver,
                                                                      **self.args['CalibrateSEMG'])
        return calibrator
        
    @context.Object(lazy_init=True)
    def Collector(self):
        return Collector.create_collector(self.window, self.signal, self.timer, self.stimuli, **self.args['Collector'])
       
    @context.Object(lazy_init=True)
    def FastPad(self):
        return FastPad.create_fastpad(self.window, self.signal, self.timer, self.stimuli,
                                     receiver_type=self.receiver, **self.args['FastPad'])
            
    @context.Object(lazy_init=True)
    def GridSpeak(self):
        return GridSpeak.create_gridspeak(self.window, self.signal, self.timer, self.stimuli,
                                          receiver_type=self.receiver, **self.args['GridSpeak'])
            
    @context.Object(lazy_init=True)
    def Dashboard(self):
        args = self.args['Dashboard']
        controllers = []
        for controller_attr in args['controllers']:
            controller = getattr(self, controller_attr)
            controllers.append(controller())
        args.pop('controllers')
        return Dashboard.create_dashboard(self.window, controllers, self.signal, self.timer,
                                          self.stimuli,  self.calibrator,
                                          receiver_type=self.receiver, **args)
        
        
class UnlockRuntime(object):
    def __init__(self):
        "Initializes the UnlockRuntime."
        self.conf = None
        self.log = None
        
        try:
            args = None
            options = None
            parser = None
            usage = "usage: %prog [options]"
            parser = OptionParser(version="%prog 1.0", usage=usage)
            conf_help = 'path to the configuration; if not set the default is used'
            fullscreen_help = 'makes the app run in fullscreen; overrides the config file setting'
            fps_help = 'displays the frequency per second; overrides the config file setting'
            vsync_help = 'turns vsync on; default is off'
            loglevel_help = 'sets the root logging level; valid values are debug, info, warn, error and critical; default value is warn; overrides the config file setting'
            signal_help = 'selects the signaling system; valid values are: random, mobilab, enobio and audio; default value is random; overrides the config file setting'
            stimuli_help = 'sets the system to use a shared stimuli; valid values are: ssvep, msequence and semg'
            mac_addr_help = 'a comma separated list of hexidecimal values that are required to connect to some signaling devices;for example -m "0x1,0x2,0x3,0x4,0x5,0x6"'
            receiver_help = 'sets the type of receiver; valid values = delta, raw, classified, datagram and multiprocess'
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
            parser.add_option('-n', '--fullscreen', default=None, action='store_true', dest='fullscreen', metavar='FULLSCREEN', help=fullscreen_help)
            parser.add_option('-f', '--fps', default=None, action='store_true', dest='fps', metavar='FPS', help=fps_help)
            parser.add_option('-v', '--vsync', default=None, action='store_true', dest='vsync', metavar='VSYNC', help=vsync_help)
            parser.add_option('-l', '--logging-level', type=str, dest='loglevel', metavar='LEVEL', help=loglevel_help)
            parser.add_option('-s', '--signal', dest='signal', default=None, type=str, metavar='SIGNAL', help=signal_help)
            parser.add_option('-t', '--stimuli', type=str, dest='stimuli', default=None, metavar='STIMULI', help=stimuli_help)
            parser.add_option('-m', '--mac-addr', dest='mac_addr', default=None, type=str, metavar='MAC-ADDR', help=mac_addr_help)
            parser.add_option('-r', '--receiver', dest='receiver', default=None, type=str, metavar='RECEIVER', help=receiver_help)
            valid_levels = { 'debug' : logging.DEBUG, 'info' : logging.INFO, 'warn' : logging.WARN, 'error' : logging.ERROR, 'critical' : logging.CRITICAL}
            (options, args) = parser.parse_args()
        except Exception as e:
            raise e
        
        try:
            self.conf = options.conf
            self.args = self.__parse_conf__()
            if options.fullscreen != None:
                self.args['fullscreen'] = options.fullscreen
            if options.fps != None:    
                self.args['fps'] = options.fps
            if options.signal != None:
                self.args['signal'] = options.signal
            if options.vsync != None:
                self.args['vsync'] = options.vsync
            if options.mac_addr != None:
                self.args['mac_addr'] = options.mac_addr
            if options.stimuli != None:
                self.args['stimuli'] = options.stimuli
            if options.receiver != None:
                self.args['receiver'] = options.receiver
                
            self.__configure_logging__()
            self.__create_controllers__()
            
        except:
            print('UnlockRuntime: WARNING logging has not been setup yet')
            print('UnlockRuntime: FATAL failed to initialize correctly')
            if parser:
                parser.print_help()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
            sys.exit(1)
         
    def __parse_conf__(self):
        with open(self.conf, 'rt') as file_descriptor:
            json_string = file_descriptor.read()
            args = json.loads(json_string)
            
        return args            
         
    def __create_controllers__(self):
        for controller in self.args['controllers']:
            self.args[controller['name']] = controller['args']
        
        self.factory = UnlockFactory(self.args)
        self.app_ctx = context.ApplicationContext(self.factory)
    
        # XXX - need to integrate the json config into the context.
        #if self.args['receiver'] == 'delta':
        #    self.factory.signal = self.app_ctx.get_object('random')
        #else:    
        self.factory.signal = self.app_ctx.get_object(self.args['signal'])
            
        self.factory.window = self.app_ctx.get_object('PygletWindow')
        if 'stimuli' in self.args.keys():
            self.factory.stimuli = self.app_ctx.get_object(self.args['stimuli'])
                
        self.main = self.app_ctx.get_object(self.args['main'])
            
    def __configure_logging__(self):
        # The Logging-Config object determines the configuration of the logging
        # System.  It follows the standard Python JSON logging config; see
        # http://docs.python.org/2/howto/logging-cookbook.html for more details.        
        if 'logging' in self.args:
            #import sys
            #print("Arages = ", self.args['logging'], file=sys.stderr)
            logging.config.dictConfig(self.args['logging'])
        else:
            logging.basicConfig(level=log_level)
            
    def start(self):
        """Starts the UnlockRuntime."""
        self.main.activate()
        self.main.window.start()
        self.main.window.close()
        
        
if __name__ == '__main__':
    unlock = UnlockRuntime()
    unlock.start()
