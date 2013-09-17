from core.acquisition import UnlockAcquisition
import numpy as np
import time

class FileDAQ(UnlockAcquisition):
    """ A file-based virtual hardware device. This is primarily for simulating
     online data presentation from recorded offline data.
    """
    def __init__(self, filename, channels, frequency, delimiter='\t'):
        super(FileDAQ, self).__init__(None, channels, frequency)

        self._filename = filename
        self._delimiter = delimiter
        self._data = None
        self._samples = None
        self._cursor = 0
        self._running = False

    def open(self, *args):
        self._data = np.genfromtxt(self._filename, delimiter=self._delimiter)
        return True

    def init(self, *args):
        self._cursor = 0
        self._samples = None
        return True

    def start(self):
        self._running = True
        return self._running

    def stop(self):
        self._running = False
        return True

    def close(self):
        self._data = None
        return True

    def acquire(self):
        if self._cursor >= self._data.shape[0]:
            return False
        self._samples = self._data[self._cursor,0:self.channels]
        self._cursor += 1
        if self.frequency > 0:
            time.sleep(1.0/self.frequency)
        return True

    def getdata(self):
        return self._samples.reshape((1,self.channels))