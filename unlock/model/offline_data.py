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

from unlock.model.model import UnlockModel
import numpy as np
import logging
import time


class OfflineData(UnlockModel):
    def __init__(self, output_file_prefix, cache_size=1):
        super(UnlockModel, self).__init__()
        self.output_file_prefix = output_file_prefix
        self.file_handle = None
        self.logger = logging.getLogger(__name__)
        self.cache = list(range(cache_size))
        self.cache_size = cache_size
        self.current = 0
        
    def process_command(self, command):
        assert self.file_handle != None
        np.savetxt(self.file_handle, command.matrix, fmt='%d', delimiter='\t')
        self.cache[self.current] = command.matrix
        self.current = 0 if (self.current % self.cache_size) == 0 else self.current + 1        
        
    def get_state(self):
        raise NotImplementedError()

    def start(self):
        assert self.file_handle == None
        self.file_handle = open("%s_%d.txt" % (self.output_file_prefix, time.time()), 'wb')
            
    def stop(self):
        assert self.file_handle != None
        self.file_handle.flush()
        self.file_handle.close()
        self.file_handle = None
        
class NonBlockingOfflineData(UnlockModel):
    def __init__(self):
        raise NotImplementedError()