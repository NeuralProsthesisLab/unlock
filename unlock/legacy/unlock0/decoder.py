import numpy as np
import time
from hsd import HarmonicSumDecision

class BCI():
    def __init__(self, daq, decider=None, selector=None, logfile=None):
        self.daq = daq
        self.decider = decider
        self.selector = selector
        self.logging = False
        if logfile is not None:
            self.logging = True
            self.fh = open("%s_%d.txt" % (logfile, time.time()), 'a')
            self.buffer = np.zeros((30*daq.frequency, daq.channels+1))
            self.cursor = 0

    def run(self):
        if not self.daq.open():
            raise Exception('DAQ device did not open')
        if not self.daq.init():
            raise Exception('DAQ device did not initialize')
        if not self.daq.start():
            raise Exception('DAQ device did not start streaming')

        correct = 0
        total = 0
        while daq.acquire():
            samples = daq.getdata()
            if self.logging:
                self.log(samples)
            d = self.decider.process(samples)
            if d is not None:
                total += 1
                if d == 0:
                    correct += 1
        print "%.2f" % (1.0*correct / total)

        if self.logging:
            np.savetxt(self.fh, self.buffer[0:self.cursor,:],
                       fmt='%d', delimiter='\t')
            self.fh.close()

        if not self.daq.stop():
            raise Exception('DAQ device encountered an error stopping')
        if not self.daq.close():
            raise Exception('DAQ device encountered an error closing')

    def log(self, samples):
        s = samples.shape[0]
        if self.cursor + s >= self.buffer.shape[0]:
            np.savetxt(self.fh, self.buffer[0:self.cursor,:],
                       fmt='%d', delimiter='\t')
            self.cursor = 0
        self.buffer[self.cursor:self.cursor+s,0:-1] = samples
        self.buffer[self.cursor:self.cursor+s,-1] = time.time()*1000
        self.cursor += s

if __name__ == '__main__':
    from daq_file import FileDAQ
    daq = FileDAQ('/Users/bgalbraith/Dropbox/School/enobio data/12hz_test.txt', 8, 0)
    hsd = HarmonicSumDecision([12.0,13.0,14.0,15.0], 4.0, 500, 8)
    bci = BCI(daq, decider=hsd)
    bci.run()