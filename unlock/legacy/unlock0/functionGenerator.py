import socket
import time
import json
import numpy as np

class functionGenerator():
    def __init__(self, numchan=1, frequency=12, amplitude=10, phase=0, fs=256,
                 dur=2):

        self.sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock3.settimeout(0.001)

        self.numchan    = numchan
        self.frequency  = frequency
        self.amplitude  = amplitude
        #self.w          = 2*np.pi*frequency
        self.phase      = phase
        self.fs         = fs
        self.dur        = dur
        self.numsamp    = fs*dur

    def sendto_file(self):
        sinWave=np.zeros([self.numchan,self.numsamp])
        tstep=0
        while tstep<numsamp+1:
            for j in range(self.numchan):
                a=self.amplitude*np.sin(2*np.pi*self.frequency*tstep/self.fs+self.phase)
                sinWave[j, tstep-1] = a
            tstep=tstep+1
#        np.save('SinWave',sinWave)
        return sinWave

    def sendto_port(self):
        sinWave=np.zeros(self.numchan)
        tstep = 0
        while tstep >=0:
            for j in range(self.numchan):
                a=self.amplitude*np.sin(2*np.pi*self.frequency*tstep/self.fs+self.phase)
                #            sinWave2 = np.roll(sinWave[j::], 1,)
                sinWave[j] = a
            tstep=tstep+1

            s = json.dumps(sinWave.tolist())
            self.sock3.sendto(s,('127.0.0.1',33447))

            time.sleep(1.0/256.0)
        self.sock3.close()


if __name__ == '__main__':
    FG = functionGenerator()
    FG.sendto_port()

