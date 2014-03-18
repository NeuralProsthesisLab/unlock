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
from unlock.util.dispatcher import *
from unlock.util.decorator import *
from unlock.util.misc import *
from unlock.util.observable import *
from unlock.util.saferef import *
from unlock.util.sockets import *
from unlock.util.signal import *
from unlock.util.factory import *
from unlock.util.injector import *
import json
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

