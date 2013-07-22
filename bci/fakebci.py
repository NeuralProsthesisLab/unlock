import sys
import random


class FakeBCI(object):
    def __init__(self):
        self.rand = random.Random(1337)
        self.getdata_count = 0
        self.acquire_count = 0
        self.ret = None
        
    def open(self, port):
        self.port = port
        return 1
        
    def init(self, analog_channels, digital_channels):
        self.init = True
        self.achan = analog_channels
        self.dchan = digital_channels
        return 1
        
    def start(self):
        self.start = True
        return 1
        
    def acquire(self):
        self.acquire_count += 1
        return 1
        
    def getdata(self, chans):
        self.getdata_count += 1
        self.last_chans = chans
        self.ret = []        
        for i in range(chans):
            self.ret.append(self.rand.randint(1, sys.maxint))
        return self.ret
        
        