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
from unlock.bci import UnlockCommandReceiverFactory, InlineBciWrapper, MultiProcessBciWrapper, UnlockDecoderFactory
from unlock.controller import PygletWindow, UnlockDashboard, UnlockControllerFactory, Canvas
from optparse import OptionParser
from sqlalchemy import create_engine


class UnlockFactory(context.PythonConfig):
    def __init__(self, config):
        super(UnlockFactory, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.mac_addr = None
        self.com_port = None
        self.window = None
        self.calibrator = None
        self.stimuli = None
        self.receiver_factory = UnlockCommandReceiverFactory()
        self.decoder_factory = UnlockDecoderFactory()
        
    @context.Object(lazy_init=True)
    def inline(self):
        # XXX - fix crimes against nature
        if 'receiver' in self.config.keys():
            self.receiver = self.config['receiver']
        else:
            self.receiver = 'inline'
            
        bci_wrapper = InlineBciWrapper(self.receiver, self.signal, self.timer)
        return bci_wrapper
    
    @context.Object(lazy_init=True)
    def create_decoder(decoder_type):
        self.decoder_type = self.decoder_factory.map_decoder(self.config['bci']['decision_type'])
        print("Decoder ", self.config['bci']['decoder'])
        import sys
        sys.exit(0)
        self.decoder = self.decoder_factory.create_decoder(self.decoder_type, self.config['bci']['decoder'])
    
    @context.Object(lazy_init=True)
    def create_command_receiver(self):
        self.command_receiver = self.receiver_factory.create_receiver(self.receiver_type,
            self.signal, self.timer, self.decoder)
        self.command_receiver.stop()
        
    @context.Object(lazy_init=True)
    def multiprocess(self):
        bci_wrapper = MultiProcessBciWrapper(self.config)
        return bci_wrapper
        
    @context.Object(lazy_init=True)        
    def ssvep(self):
        canvas = UnlockControllerFactory.create_canvas(self.window.width, self.window.height)
        stimuli = UnlockControllerFactory.create_quad_ssvep(canvas, self.bci_wrapper)
        return stimuli
     
    @context.Object(lazy_init=True)
    def nidaq(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_nidaq_signal(self.timer)
        if not signal.start():
            raise RuntimeError('Failed to start National Instruments DAQ')
        return signal
        #for j in range(50):
        #	ret = daq.acquire()
        #	ret = daq.getdata(ret)
        #	f = open('test.data', 'wb')
        #	import numpy as np
        #	a = np.array(ret, dtype='float64')
        #	a = a.reshape((500, 4))
        #	#np.savetxt(f, a, fmt='%d', delimiter='\t')
        #	for i in range(20):
        #		print(a[i])
        #        
        
    @context.Object(lazy_init=True)        
    def audio(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.AudioSignal()
        
        if not signal.start():
            raise RuntimeError('failed to start audio signal')
            
        return signal        
        
    @context.Object(lazy_init=True)    
    def enobio(self):
        mac_addr = None
        if 'mac_addr' in self.config.keys():
            mac_addr = [int(value,0) for value in [x.strip() for x in self.config['mac_addr'].split(',')]]
        
        if mac_addr is None:
            print('enobio requires a mac address; none set')
            raise RuntimeError('enobio requires a mac address; none set')
        
        from unlock.bci import acquire
        # XXX - h4x0r        
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_enobio_signal(self.timer)
        if not signal.open(mac_addr):
            print('enobio did not open')
            raise RuntimeError('enobio did not open')
        if not signal.start():
            print('enobio device did not start streaming')                                 
            raise RuntimeError('enobio device did not start streaming')                       
        return signal
        
    @context.Object(lazy_init=True)    
    def mobilab(self):
        com_port = None
        if 'com_port' in self.config.keys():
            com_port = self.config['com_port']
            
        if com_port is None:
            print('mobilab requires a com port; none set')
            raise RuntimeError('mobilab requires a com port; none set')
            
        analog_channels_bitmask = 1+2+4+8+16+32+64+128
        from unlock.bci import acquire    
        # XXX - h4x0r
        self.timer = acquire.create_timer()
        signal = acquire.create_nonblocking_mobilab_signal(
            self.timer, analog_channels_bitmask, 0, com_port)
            
        if not signal.start():
            print('mobilab device did not start streaming') 
            raise RuntimeError('mobilab device did not start streaming')                       
        return signal
        
    @context.Object(lazy_init=True)
    def file(self):
        from unlock.bci import acquire
        # XXX - h4x0r        
        self.timer = acquire.create_timer()
        raise Exception("FIX ME")
        signal = acquire.MemoryResidentFileSignal('analysis/data/valid/emg_signal_1380649383_tongue_c.5_r.5_i1.txt',
            self.timer, channels=17)
        if not signal.start():
            print('file signal failed to start; filename = ', self.config['filename'])
            raise RuntimeError('file signal failed to start')
        return signal
            
    @context.Object(lazy_init=True)
    def random(self):
        from unlock.bci import acquire
        self.timer = acquire.create_timer()
        signal = acquire.create_random_signal(self.timer)
        signal.open([])
        signal.start()
        return signal
            
    @context.Object(lazy_init=True)
    def pyglet_window(self):
        return PygletWindow(self.bci_wrapper, self.config['fullscreen'], self.config['fps'],
            self.config['vsync'])
    # XXX     
    #@context.Object(lazy_init=True)
    #def CalibrateFacialEMGDetector(self):
    #    raise Exception("FIX ME")
    #    self.calibrator, calibrator = Calibrate.create_smg_calibrator(self.window,
    #        self.command_receiver, **self.config['CalibrateFacialEMGDetector'])
    #    return calibrator
    #        
    #@context.Object(lazy_init=True)
    #def FacialEMGCollector(self):
    #    return Collector.create_mouth_based_emg_collector(self.window, self.bci_wrapper, self.stimuli,
    #        **self.config['FacialEMGCollector'])
    #       
    #@context.Object(lazy_init=True)
    #def FastPad(self):
    #    return FastPad.create_fastpad(self.window, self.bci_wrapper, self.stimuli, **self.config['FastPad'])
    #        
    #@context.Object(lazy_init=True)
    #def GridSpeak(self):
    #    raise Exception("FIX ME")
    #    return GridSpeak.create_gridspeak(self.window, self.bci_wrapper, self.stimuli,
    #        **self.config['GridSpeak'])
    #        
    #@context.Object(lazy_init=True)
    #def GridCursor(self):
    #    raise Exception("FIX ME")        
    #    return GridCursor.create_gridcursor(self.window, self.bci_wrapper, self.stimuli,
    #        **self.config['GridCursor'])
    #        
    #@context.Object(lazy_init=True)
    #def TimeScope(self):
    #    return UnlockControllerFactory.create_time_scope(self.window, self.bci_wrapper, self.stimuli,
    #        **self.config['TimeScope'])
    #        
    #@context.Object(lazy_init=True)
    #def FrequencyScope(self):
    #    return UnlockControllerFactory.create_frequency_scope(self.window, self.bci_wrapper, self.stimuli,
    #        **self.config['FrequencyScope'])
            
    @context.Object(lazy_init=True)
    def ssvep_diagnostic(self):
        return UnlockControllerFactory.create_standalone_ssvep_diagnostic(self.window, self.bci_wrapper,
            **self.config['ssvep_diagnostic'])
    
    @context.Object(lazy_init=True)
    def single_ssvep_diagnostic(self):
        print ("config = ", self.config['single_ssvep_diagnostic'], self.config['single_ssvep_diagnostic'])
        return UnlockControllerFactory.create_single_standalone_ssvep_diagnostic(self.window, self.bci_wrapper,
            **self.config['single_ssvep_diagnostic'])
        
    @context.Object(lazy_init=True)
    def dashboard(self):
        config = self.config['dashboard']
        controllers = []
        for controller_attr in config['controllers']:
            controller = getattr(self, controller_attr)
            controllers.append(controller())
        config.pop('controllers')
        return UnlockControllerFactory.create_dashboard(self.window, controllers, self.bci_wrapper, self.stimuli,
            self.calibrator, **config)
            
            
class UnlockRuntime(object):
    def __init__(self):
        """Initializes the UnlockRuntime."""
        self.conf = None
        self.logger = None
        
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
            mac_addr_help = 'a comma separated list of hexadecimal values that are required to connect to some signaling devices;for example -m "0x1,0x2,0x3,0x4,0x5,0x6"'
            com_port_help = 'the COM port associated with some data acquisition devices; e.g. -p COM3'
            receiver_help = 'sets the type of receiver; valid values include delta, raw, decoded and datagram'
            bci_wrapper_help = 'sets the type of bci_wrapper; valid values include inline and multiprocess'
            unrecorded_help = 'turns off recording'
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
            parser.add_option('-n', '--fullscreen', default=None, action='store_true', dest='fullscreen', metavar='FULLSCREEN', help=fullscreen_help)
            parser.add_option('-f', '--fps', default=None, action='store_true', dest='fps', metavar='FPS', help=fps_help)
            parser.add_option('-v', '--vsync', default=None, action='store_true', dest='vsync', metavar='VSYNC', help=vsync_help)
            parser.add_option('-l', '--logging-level', type=str, dest='loglevel', default=None, metavar='LEVEL', help=loglevel_help)
            parser.add_option('-s', '--signal', dest='signal', default=None, type=str, metavar='SIGNAL', help=signal_help)
            parser.add_option('-t', '--stimuli', type=str, dest='stimuli', default=None, metavar='STIMULI', help=stimuli_help)
            parser.add_option('-m', '--mac-addr', dest='mac_addr', default=None, type=str, metavar='MAC-ADDR', help=mac_addr_help)
            parser.add_option('-p', '--com-port', dest='com_port', default=None, type=str, metavar='COM-PORT', help=com_port_help)
            parser.add_option('-r', '--receiver', dest='receiver', default=None, type=str, metavar='RECEIVER', help=receiver_help)
            parser.add_option('-d', '--bci_wrapper', dest='bci_wrapper', default=None, type=str, metavar='BCI_WRAPPER', help=bci_wrapper_help)
            parser.add_option('-u', '--unrecorded', default=None, action='store_true', dest='unrecorded', metavar='UNRECORDED', help=unrecorded_help)
            valid_levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR, 'critical': logging.CRITICAL}
            self.loglevel = logging.INFO
            (options, args) = parser.parse_args()
        except Exception as e:
            raise e
            
        try:
            self.conf = options.conf
            self.config = self.__parse_conf__()
            if options.fullscreen is not None:
                self.config['fullscreen'] = options.fullscreen
            if options.fps is not None:
                self.config['fps'] = options.fps
            if options.signal is not None:
                self.config['signal'] = options.signal
            if options.vsync is not None:
                self.config['vsync'] = options.vsync
            if options.mac_addr is not None:
                self.config['mac_addr'] = options.mac_addr
            if options.com_port is not None:
                self.config['com_port'] = options.com_port
            if options.stimuli is not None:
                self.config['stimuli'] = options.stimuli
            if options.receiver is not None:
                self.config['receiver'] = options.receiver
            if options.bci_wrapper is not None:
                self.config['bci_wrapper'] = options.bci_wrapper
            if options.loglevel is not None:
                # Config file settings override this command line parameter
                self.loglevel = valid_levels[options.loglevel]
            if options.unrecorded is not None:
                self.config['unrecorded'] = options.unrecorded
                
            self.__configure_logging__()
            self.logger.info('Logging setup successfully completed')
            database = self.config['database']
            self.__configure_persistence__(database['host'], database['user'],database['name'],
                database['port'], database['addr'])            
            self.logger.info('Database setup successfully completed')                
            self.__create_controllers__()
            self.logger.info('Unlock setup successfully completed')                
            
        except:
            if self.logger == None:
                print('UnlockRuntime: FATAL failed to initialize correctly')
            else:
                self.logger.fatal('failed to initialize correctly')
                
            if parser:
                parser.print_help()
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
            sys.exit(1)
         
    def __parse_conf__(self):
        with open(self.conf, 'rt') as file_descriptor:
            json_string = file_descriptor.read()
            config = json.loads(json_string)
        return config            
         
    def __create_controllers__(self):
        for controller in self.config['controllers']:
            self.config[controller['name']] = controller['args']
        
        self.factory = UnlockFactory(self.config)
        self.app_ctx = context.ApplicationContext(self.factory)
    
        if self.config['bci_wrapper'] == 'inline':
            self.factory.signal = self.app_ctx.get_object(self.config['signal'])
            self.decoder = self.app_ctx.get_object(self.config['decoder'])
            
        self.factory.bci_wrapper = self.app_ctx.get_object(self.config['bci_wrapper'])
        
        self.factory.window = self.app_ctx.get_object('PygletWindow')
        if 'stimuli' in self.config.keys():
            self.factory.stimuli = self.app_ctx.get_object(self.config['stimuli'])
        self.main = self.app_ctx.get_object(self.config['main'])
        
    def __configure_persistence__(self, host, name, user, port, addr):
        if 'unrecorded' in self.config:
            self.engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (user, addr, host, port, name))
            return self.engine
        
    def __configure_logging__(self):
        # The Logging-Config object determines the configuration of the logging
        # System.  It follows the standard Python JSON logging config; see
        # http://docs.python.org/2/howto/logging-cookbook.html for more details.        
        if 'logging' in self.config:
            logging.config.dictConfig(self.config['logging'])
        else:
            logging.basicConfig(level=self.loglevel)
            
        self.logger = logging.getLogger(__name__)
                
    def start(self):
        """Starts the UnlockRuntime."""
        self.main.activate()
        self.logger.info('Starting Unlock...')                        
        self.main.window.start()
        self.main.window.close()
        
        
if __name__ == '__main__':
    #import psutil
    #import os
    #p = psutil.Process(os.getpid())
    #p.set_nice(psutil.HIGH_PRIORITY_CLASS)
    unlock = UnlockRuntime()
    unlock.start()
