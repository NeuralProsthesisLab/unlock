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
from unlock.util.observable import *
from unlock.util.saferef import *
from unlock.util.injector import *
from optparse import OptionParser
import json
import logging
import logging.config
import sys

__author__ = 'jpercent'


class RuntimeAssistant(object):
    def __init__(self):
        super(RuntimeAssistant, self).__init__()

    @staticmethod
    def configure(config, fact_instance):
        assert fact_instance
        dpi = DependencyInjector(fact_instance)
        instance = dpi.configure_application(config)
        assert instance
        return instance

    @staticmethod
    def parse_json_config(conf):
        with open(conf, 'rt') as file_descriptor:
            json_string = file_descriptor.read()
            config = json.loads(json_string)
        return config

    @staticmethod
    def make_high_priority():
        '''Makes the Unlock process a high priority; the impact of this was never investigated and it is not used.'''
        try:
            import psutil
            import os
            p = psutil.Process(os.getpid())
            p.set_nice(psutil.HIGH_PRIORITY_CLASS)
        except Exception as e:
            RuntimeAssistant.print_last_exception()

    @staticmethod
    def print_last_exception():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)


class JsonConfiguredRuntime(object):
    def __init__(self, factory, path_to_default_config):
        """Initializes a JsonConfiguredRuntime."""
        self.factory = factory
        self.conf = None
        self.logger = None
        self.loglevel = logging.INFO
        self.config = None
        self.runtime_instance = None
        self.args = None
        self.options = None
        self.parser = None
        self.usage = "usage: %prog [options]"

        conf_help = 'path to the configuration; if not set conf.json is used'

        try:
            self.parser = OptionParser(version="%prog 1.0", usage=self.usage)
            self.default_conf = os.path.join(path_to_default_config, 'conf.json')
            self.parser.add_option('-c', '--conf', type=str, dest='conf', default=self.default_conf, metavar='CONF', help=conf_help)
        except Exception as e:
            print(str(self.__class__.__name__)+': FATAL failed to parse program arguments')
            RuntimeAssistant.print_last_exception()
            raise e

    def init(self):
        assert self.parser
        try:
            (self.options, self.args) = self.parser.parse_args()
            assert self.options.conf
            self.config = RuntimeAssistant.parse_json_config(self.options.conf)
            self.runtime_instance = RuntimeAssistant.configure(self.config, self.factory)

        except Exception as e:
            if not self.logger:
                print(str(self.__class__.__name__)+': FATAL failed to initialize correctly; did not complete logging setup')
            else:
                self.logger.fatal('failed to initialize correctly')

            if self.parser:
                self.parser.print_help()

            RuntimeAssistant.print_last_exception()
            raise e
        self.logger = logging.getLogger(__name__)

