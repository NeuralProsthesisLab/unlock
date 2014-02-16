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
        
        conf_help = 'path to the configuration; if not set conf.json is used'
        
        try:
            
            parser = OptionParser(version="%prog 1.0", usage=usage)
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
            (options, args) = parser.parse_args()
            
        except Exception as e:
            print('UnlockRuntime.__init__: FATAL failed to parse program arguments')
            UnlockRuntime.print_last_exception()
            raise e
            
        try:
            
            self.config = UnlockRuntime.setup_config(options)
            self.configure(self.config)
            
        except Exception as e:
            if not self.logger:
                print('UnlockRuntime.__init__: FATAL failed to initialize correctly; did not complete logging setup')
            else:
                self.logger.fatal('failed to initialize correctly')
                
            if parser:
                parser.print_help()
                
            UnlockRuntime.print_last_exception()
            raise e

    @staticmethod
    def setup_config(options):
        config = UnlockRuntime.parse_config(options.conf)
        return config

    @staticmethod
    def parse_config(conf):
        with open(conf, 'rt') as file_descriptor:
            json_string = file_descriptor.read()
            config = json.loads(json_string)
        return config            

    def configure(self, config):
        factory = UnlockFactory()
        level = 0
        max_level = 0
        while level <= max_level:
            for key, value in config.items():
                level_value = value['singleton']
                if level_value > max_level:
                    max_level = level_value
                    
                if level_value <= level:
                    factor.create_singleton(name, key, config)
                    config.pop(key)
                    
            level += 1
        
        for obj in config:
            if obj['main']:
                newobj = factory.create(obj, config)
                assert not self.main
                self.unlock = newobj
                return self.unlock                    
                
                
    @staticmethod
    def make_high_priority():
        '''Makes the Unlock process a high priority; the impact of this was never investigated and it is not used.'''
        try:
            import psutil
            import os
            p = psutil.Process(os.getpid())
            p.set_nice(psutil.HIGH_PRIORITY_CLASS)
        except Exception as e:
            UnlockRuntime.print_last_exception()

    @staticmethod
    def print_last_exception():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    def start(self):
        """Starts the UnlockRuntime."""
        # XXX - this is weird we shouldn't reach in and call window start ater activate.  unlock_instance should
        # override activate.  then call the super.activate then call window.start.  then overrride deactiveate to be
        # window.close which gets called here.
        self.unlock.activate()
        self.logger.info('Starting Unlock...')                        
        self.unlock.window.start()
        self.unlock.window.close()


if __name__ == '__main__':
    try:
        unlock = UnlockRuntime()
        unlock.start()
    except:
        sys.exit(1)

