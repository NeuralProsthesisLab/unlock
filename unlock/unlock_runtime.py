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

import unlock

from optparse import OptionParser
from unlock.util import RuntimeAssistant


class UnlockRuntime(object):
    def __init__(self, unlock_factory=None):
        """Initializes the UnlockRuntime."""
        self.factory = unlock_factory
        self.conf = None
        self.logger = None
        self.loglevel = logging.INFO
        self.config = None
        self.unlock = None
        self.args = None
        self.options = None
        self.parser = None
        self.usage = "usage: %prog [options]"
        
        conf_help = 'path to the configuration; if not set conf.json is used'

        try:
            self.parser = OptionParser(version="%prog 1.0", usage=self.usage)
            conf = os.path.join(os.path.dirname(inspect.getfile(UnlockRuntime)), 'conf.json')
            self.parser.add_option('-c', '--conf', type=str, dest='conf', default=conf, metavar='CONF', help=conf_help)
        except Exception as e:
            print('UnlockRuntime.__init__: FATAL failed to parse program arguments')
            RuntimeAssistant.print_last_exception()
            raise e

    def init(self):
        assert self.parser
        try:
            (self.options, self.args) = self.parser.parse_args()
            self.config = RuntimeAssistant.parse_json_config(self.options.conf)
            self.unlock = RuntimeAssistant.configure(self.config, self.factory)
        except Exception as e:
            if not self.logger:
                print('UnlockRuntime.__init__: FATAL failed to initialize correctly; did not complete logging setup')
            else:
                self.logger.fatal('failed to initialize correctly')

            if self.parser:
                self.parser.print_help()

            RuntimeAssistant.print_last_exception()
            raise e
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Starts the UnlockRuntime."""
        assert self.unlock
        self.unlock.activate()
        self.logger.info('Starting Unlock...')
        self.unlock.window.start()
        self.unlock.window.close()

if __name__ == '__main__':
    factory_instance = unlock.UnlockFactory()
    unlock = UnlockRuntime(factory_instance)
    unlock.init()
    unlock.run()


