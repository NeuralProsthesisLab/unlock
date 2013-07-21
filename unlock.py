import os
import logging.config
import traceback
import json
import sys
import inspect

from optparse import OptionParser


class UnlockRuntime(object):
    def __init__(self):
        "Initializes the UnlockRuntime."
        self.conf_path = None
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
            bci_help = 'selects the BCI; valid values are: fake, mobilab, enobio; default value is fake; overrides the config file setting'
    
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
            parser.add_option('-n', '--fullscreen', default=False, action='store_true', dest='fullscreen', metavar='FULLSCREEN', help=fullscreen_help)
            parser.add_option('-f', '--fps', default=False, action='store_true', dest='fps', metavar='FPS', help=fps_help)
            parser.add_option('-l', '--logging-level', type=str, dest='loglevel', metavar='LEVEL', help=loglevel_help)
            parser.add_option('-b', '--bci', dest='bci', default='fake', type=str, metavar='BCI', help=bci_help)        
            valid_levels = { 'debug' : logging.DEBUG, 'info' : logging.INFO, 'warn' : logging.WARN, 'error' : logging.ERROR, 'critical' : logging.CRITICAL}
            (options, args) = parser.parse_args()
                
            self.conf = options.conf
            self.parse_conf()
            self.create_controllers()
            
        except:
            if parser:
                parser.print_help()
                
            msg = "UnlockRuntime: failed to initialize correctly"
            if self.log:
                log.exception(msg)
            else:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)                
                
                
                sys.exit(1)
                
    def parse_conf(self):
        self.app_ctx = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'app-ctx.xml')
        with open(self.conf, 'rt') as file_descriptor:
            json_binary = file_descriptor.read()
            self.conf = json.loads(json_binary)        
        print 'conf ------>',self.conf, '<------------------------------------'
        self.app_ctx = self.conf['Application-Context']
        self.logging_conf = self.conf['Logging-Config']
        print 'logging -------------------------->', self.logging_conf, '<------------------------------------'
        print 'App Context -------------------------->', self.app_ctx, '<------------------------------------'
        
    def create_controllers(self):
        for controller in self.controllers:
            #if controller
            print "name", name

        
    def setup_logging(self):
        """Setup logging configuration """
        pass
#            logging.config.dictConfig(json_string)
#        else:
#            logging.basicConfig(level=log_level)

    def start(self):
        pass
    
    @staticmethod
    def create():
        print "create called"
    
if __name__ == '__main__':
    unlock = UnlockRuntime()
    unlock.start()
