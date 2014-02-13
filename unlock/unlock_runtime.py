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

from unlock import UnlockFactory
from optparse import OptionParser
from sqlalchemy import create_engine


class UnlockRuntime(object):
    def __init__(self):
        """Initializes the UnlockRuntime."""
        self.conf = None
        self.logger = None
        self.loglevel = logging.INFO

        args = None
        options = None
        parser = None
        usage = "usage: %prog [options]"

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
        unrecorded_help = 'turns off recording'

        valid_levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR, 'critical': logging.CRITICAL}

        try:
            parser = OptionParser(version="%prog 1.0", usage=usage)
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
            parser.add_option('-u', '--unrecorded', default=None, action='store_true', dest='unrecorded', metavar='UNRECORDED', help=unrecorded_help)
            (options, args) = parser.parse_args()
        except Exception as e:
            print('UnlockRuntime: FATAL failed to parse program arguments')
            self.print_last_exception()
            sys.exit(1)

        try:
            self.setup_config(options, valid_levels)
            self.configure()
        except Exception as e:
            if self.logger == None:
                print('UnlockRuntime: FATAL failed to initialize correctly; did not complete logging setup')
            else:
                self.logger.fatal('failed to initialize correctly')
                
            if parser:
                parser.print_help()

            self.print_last_exception()
            sys.exit(1)

    def setup_config(self, options, valid_levels):
        self.conf = options.conf
        self.config = self.parse_config()

        assert 'bci' in self.config.keys()
        assert 'signal' in self.config['bci'].keys()
        assert 'pyglet' in self.config.keys()
        assert 'main' in self.config.keys()
        assert 'controllers' in self.config.keys()
        
        if options.fullscreen is not None:
            self.config['pyglet']['fullscreen'] = options.fullscreen
        if options.fps is not None:
            self.config['pyglet']['fps'] = options.fps
        if options.vsync is not None:
            self.config['pyglet']['vsync'] = options.vsync
            
        if options.signal is not None:
            self.config['signal'] = options.signal
        if options.mac_addr is not None:
            self.config['signal']['mac_addr'] = options.mac_addr
        if options.com_port is not None:
            self.config['signal']['com_port'] = options.com_port
            
        if options.stimuli is not None:
            self.config['stimuli'] = options.stimuli
            
        if options.receiver is not None:
            self.config['bci']['receiver'] = options.receiver
        if options.bci_wrapper is not None:
            self.config['bci']['wrapper'] = options.bci_wrapper
            
        if options.loglevel is not None and options.loglevel in valid_levels:
            # Config file settings override this command line parameter
            self.loglevel = valid_levels[options.loglevel]
            
        if options.unrecorded is not None:
            self.config['unrecorded'] = options.unrecorded
            
    def parse_config(self):
        with open(self.conf, 'rt') as file_descriptor:
            json_string = file_descriptor.read()
            config = json.loads(json_string)
        return config            
            
    def configure(self):
        self.configure_logging()
        self.logger.info('Logging setup successfully completed')
        
        self.configure_persistence()
        self.logger.info('Database setup successfully completed')                
        
        self.unlock = self.create_unlock()
        self.logger.info('Unlock setup successfully completed')                
            
    def configure_logging(self):
        # The Logging-Config object determines the configuration of the logging
        # System.  It follows the standard Python JSON logging config; see
        # http://docs.python.org/2/howto/logging-cookbook.html for more details.        
        if 'logging' in self.config:
            logging.config.dictConfig(self.config['logging'])
        else:
            logging.basicConfig(level=self.loglevel)
            
        self.logger = logging.getLogger(__name__)
         
    def configure_persistence(self):
        db = self.config['database']
        if 'unrecorded' in self.config:
            self.engine = create_engine('postgresql://%s:%s@%s:%s/%s' % \
                (db['host'], db['user'],db['name'], db['port'], db['addr']))
                
    def create_unlock(self):
        factory = UnlockFactory()
        unlock_instance = factory.create_unlock(self.config)
        return unlock_instance

    def make_high_priority(self):
        '''Makes the Unlock process a high priority; we never researched the impact of doing this'''
        try:
            import psutil
            import os
            p = psutil.Process(os.getpid())
            p.set_nice(psutil.HIGH_PRIORITY_CLASS)
        except Exception as e:
            self.print_last_exception()

    def print_last_exception(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    def start(self):
        """Starts the UnlockRuntime."""
        # XXX - this is weird we shouldn't reach in and call window start after activate.  unlock_instance should
        # override activate.  then call the super.activate then call window.start.  then overrride deactiveate to be
        # window.close which gets called here.
        self.unlock.activate()
        self.logger.info('Starting Unlock...')                        
        self.unlock.window.start()
        self.unlock.window.close()


if __name__ == '__main__':
    unlock = UnlockRuntime()
    unlock.start()
