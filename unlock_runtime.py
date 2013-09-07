import os
import sys
import json
import traceback
import inspect

import logging
import logging.config

from unlock import context 
from unlock.controller import PygletWindow, Collector, Dashboard, SSVEP
from optparse import OptionParser


class UnlockFactory(context.PythonConfig):
    def __init__(self, args):
        super(UnlockFactory, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.args = args
        
    @context.Object(lazy_init=True)    
    def enobio(self):
        from unlock.neural import acquire
        signal = acquire.create_enobio_signal()
#        signal.channels = 8
        if not signal.open():
            print('enobio did not open')
            raise RuntimeError('enobio did not open')
        if not signal.start():
            print('enobio device did not start streaming')                                 
            raise RuntimeError('enobio device did not start streaming')                       
        return signal
    
    @context.Object(lazy_init=True)
    def random(self):
        from unlock.neural import acquire
        signal = acquire.create_random_signal()
        signal.open()
        signal.start()
        return signal
        
    @context.Object(lazy_init=True)
    def PygletWindow(self):
        return PygletWindow(self.signal, self.args['fullscreen'], self.args['fps'])
        
    @context.Object(lazy_init=True)
    def SingleMSequenceCollector(self):
        window = self.PygletWindow()
        return Collector.create_single_centered_msequence_collector(window, self.signal, **self.args['SingleMSequenceCollector'])
        
    @context.Object(lazy_init=True)
    def MultiMSequenceCollector(self):
        window = self.PygletWindow()
        return Collector.create_multi_centered_msequence_collector(window, self.signal, **self.args['MultiMSequenceCollector'])
    
    @context.Object(lazy_init=True)
    def Ssvep(self):
        window = self.PygletWindow()
        return SSVEP.create_ssvep(window, self.signal, **self.args['Ssvep'])
    
    @context.Object(lazy_init=True)
    def EmgCollector(self):
        window = self.PygletWindow()        
        return Collector.create_emg_collector(window, self.signal, **self.args['EmgCollector'])    
        
    @context.Object(lazy_init=True)
    def Dashboard(self):
        args = self.args['Dashboard']
        controllers = []
        for controller_attr in args['controllers']:
            controller = getattr(self, controller_attr)
            controllers.append(controller())
        args.pop('controllers')
        window = self.PygletWindow()
        return Dashboard.create(window, controllers, self.signal, **args)
        
        
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
            loglevel_help = 'sets the root logging level; valid values are debug, info, warn, error and critical; default value is warn; overrides the config file setting'
            signal_help = 'selects the signaling system; valid values are: fake, mobilab, enobio; default value is fake; overrides the config file setting'
            
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            
            parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
            parser.add_option('-n', '--fullscreen', default=None, action='store_true', dest='fullscreen', metavar='FULLSCREEN', help=fullscreen_help)
            parser.add_option('-f', '--fps', default=None, action='store_true', dest='fps', metavar='FPS', help=fps_help)
            parser.add_option('-l', '--logging-level', type=str, dest='loglevel', metavar='LEVEL', help=loglevel_help)
            parser.add_option('-s', '--signal', dest='signal', default=None, type=str, metavar='SIGNAL', help=signal_help)        
            valid_levels = { 'debug' : logging.DEBUG, 'info' : logging.INFO, 'warn' : logging.WARN, 'error' : logging.ERROR, 'critical' : logging.CRITICAL}
            (options, args) = parser.parse_args()
            
            self.conf = options.conf
            self.args = self.__parse_conf__()
            if options.fullscreen != None:
                self.args['fullscreen'] = options.fullscreen
            if options.fps != None:    
                self.args['fps'] = options.fps
            if options.signal != None:
                self.args['signal'] = options.signal            
            
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
        self.factory.signal = self.app_ctx.get_object(self.args['signal'])
        self.main = self.app_ctx.get_object(self.args['main'])
            
    def __configure_logging__(self):
        # The Logging-Config object determines the configuration of the logging
        # System.  It follows the standard Python JSON logging config; see
        # http://docs.python.org/2/howto/logging-cookbook.html for more details.        
        if 'logging' in self.args:
            import sys
            print("Arages = ", self.args['logging'], file=sys.stderr)
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
