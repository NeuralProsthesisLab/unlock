from decoders.hsd2 import HSD2
import socket
import numpy as np
import json

class SsvepDecoder:

    def __init__(self):

        # Settings
        self.n_electrodes = 3

        # HSD start
        self.hsd        = HSD2(fs=500,
                          ff_window=0.1,h1_window=0.1,psd_method='fft',mtp_npi=1.0,mtp_nwin=4,file_baseline="")
        self.n_samples  = self.hsd.n_samples

        # GTEC start
        # self.device = pygtec.MOBIlab()
        # isopen = self.device.open(port)
        # isinit = self.device.init(120,0) # 120 = EOG+O1+Oz+O2+EOG 8+16+32+64
        # isstarted = self.device.start()
        # if isopen == 1: print 'okay! mobilab opened'
        # if isinit == 1: print 'okay! mobilab initialized'
        # if isstarted == 1: print 'okay! mobilab started!'

        # UDP settings
        # self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )  # outgoing
        # self.sock.settimeout(0.001)
        # self.sock2 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # outgoing
        # self.sock2.settimeout(0.001)
        # self.sock3 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # outgoing
        # self.sock3.settimeout(0.001)
        self.sock4 = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # incoming
        self.sock4.settimeout(0.001)
        self.sock4.bind(('127.0.0.1',33447))

        # Initializations
        self.data_buffer    = np.zeros((self.n_electrodes,self.n_samples))
        self.buffer_idx     = 0
        self.loop_exit      = False

    def run(self):
        mu = np.zeros(3)
        while True:
        # STEP 0: Check if decoder reset needed (HACKY FOR NOW!)
            data = None
            try:
                raw, _ = self.sock4.recvfrom(128)
                data = json.loads(raw)
            except:
                continue

            # STEP 2: Add O1,Oz,O2 to data buffer (data_gtec[0] is currently EOG). Kinda hacky now.
            bipolar = [data[i] - data[i+3] for i in xrange(3)]
            #mu = 0.95*mu + 0.05*np.array(data[0:3])
            self.data_buffer[:,self.buffer_idx] = bipolar#data[0:3] - mu
            self.buffer_idx+=1

            # STEP 3: If buffer full, run the DECISION decoder then reset buffer.
            if self.buffer_idx == self.n_samples:
                hsd_winner = self.hsd.run(self.data_buffer) + 1 # add 1 to go 1-4!!!
                print 'HSD winner: ', str(hsd_winner)
                self.buffer_idx  = 0
                self.data_buffer = np.zeros((self.n_electrodes,self.n_samples))

# RUN IT!
decoder = SsvepDecoder()
decoder.run()