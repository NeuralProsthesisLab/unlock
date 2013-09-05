import sys
import random


class FakeSignal(object):
    def __init__(self, channels=4, generate_each_time=False):
        self.rand = random.Random(1337)
        self.getdata_count = 0
        self.acquire_count = 0
        self.ret = None
        self.chans = channels
        self.generate_each_time = generate_each_time
        
    def channels(self, ):
        return self.chans
        
    def open(self, port=None):
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
        
    def getdata(self, samples_cross_channels):
        self.getdata_count += 1
        if self.ret == None or self.generate_each_time:
            self.ret = []        
            for i in range(samples_cross_channels):
                self.ret.append(self.rand.randint(1, sys.maxsize))
            
        return self.ret
        
        