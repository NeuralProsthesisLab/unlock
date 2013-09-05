
from .model import UnlockModel
import numpy as np
import logging
import time


class OfflineData(UnlockModel):
    def __init__(self, output_file_prefix, cache_size=1):
        super(UnlockModel, self).__init__()
        self.output_file_prefix = output_file_prefix
        self.file_handle = open("%s_%d.txt" % (output_file_prefix, time.time()), 'wb')
        self.logger = logging.getLogger(__name__)
        self.cache = list(range(cache_size))
        self.cache_size = cache_size
        self.current = 0
        
    def process_command(self, command):
        np.savetxt(self.file_handle, command.matrix, fmt='%d', delimiter='\t')
        self.cache[self.current] = command.matrix
        self.current = 0 if (self.current % self.cache_size) == 0 else self.current + 1        
        
    def get_state(self):
        raise NotImplementedError()

    def start(self):
        if not self.file_handle:
            self.file_handle = open("%s_%d.txt" % (self.output_file_prefix, time.time()), 'wb')
            
    def stop(self):
        self.file_handle.flush()
        self.file_handle.close()
        self.file_handle = None
        
        
class NonBlockingOfflineData(UnlockModel):
    def __init__(self):
        raise NotImplementedError()