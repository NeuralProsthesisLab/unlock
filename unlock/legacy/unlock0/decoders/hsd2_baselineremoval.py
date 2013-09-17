from hsd2 import HSD2
import pygtec
import numpy as np
import argparse

__author__ = "Sean Lorenz"
__copyright__ = "Copyright 2012, Neural Prosthesis Laboratory"
__credits__ = ["Jonathan Brumberg", "Byron Galbraith", "Sean Lorenz"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "npl@bu.edu"
__status__ = "Development"

parser = argparse.ArgumentParser(description="HSD Baseline Removal Preprocessing Step")
parser.add_argument("--subject_id",action='store',default="demo",help="Subject Identifier")
parser.add_argument("--decoder_type",action='store',default="mtp",help="Decoder Type [mtp | fft]")
parser.add_argument("--com_port", action='store',default="/dev/rfcomm0",help="COM PORT for g.Tec MOBILAB")
args = parser.parse_args()

class HsdBaselineRemoval:

    def __init__(self,COM_PORT='/dev/rfcomm0',subject_id=None,decoder_type=None,n_electrodes=3,fs=256):

        # Settings
        record_time         = 60.0              # number of seconds to record
        self.n_electrodes   = n_electrodes      # number of electrodes
        self.n_samples      = fs*record_time    # number of samples to do MTP over
        self.decoder_type   = decoder_type
        self.data_file_name = 'hsdBaseline_'+subject_id+'.txt'

        # HSD start
        self.hsd            = HSD2()

        # GTEC start
        self.device = pygtec.MOBIlab()
        isopen = self.device.open(COM_PORT)
        isinit = self.device.init(120,0) # 120 = EOG+O1+Oz+O2+EOG 8+16+32+64
        isstarted = self.device.start()
        if isopen    == 1: print 'okay! mobilab opened'
        if isinit    == 1: print 'okay! mobilab initialized'
        if isstarted == 1: print 'okay! mobilab started!'

        # Initializations
        self.data_buffer    = np.zeros((self.n_electrodes,self.n_samples))
        self.buffer_idx     = 0

    def run(self):

        while self.device.acquire():

            # STEP 1: Grab data from mobilab (and send to sock3)
            data_gtec = self.device.getdata(self.n_electrodes+1)

            # STEP 2: Add O1,Oz,O2 to data buffer (data_gtec[0] is currently EOG). Kinda hacky now.
            self.data_buffer[:,self.buffer_idx] = data_gtec[1:4]
#            self.data_buffer[:,self.buffer_idx] = np.random.random(3)
            self.buffer_idx+=1

            # STEP 3: If buffer full, store, plot and save to file the PSD.
            if self.buffer_idx == self.n_samples:
                y = self.hsd.preproc(self.data_buffer)
                # MTP
                if self.decoder_type == 'mtp':
                    psd_cuts = np.zeros((15,3,513)) # cut into 4s chunks to match the MTP output
                    psd_data = np.zeros((3,513))    # MTP output for each electrode after averaging each 4s chunk
                    # split the data into 4s segments
                    for i in range(15):
                        psd_cuts[i,:,:] = self.hsd.multiTaper(y[:,i*1024:i*1024+1024])
                    for i in range(3):
                        psd_data[i,:] = np.mean(psd_cuts[:,i,:],axis=0)
                    # print the result
                    self.hsd.mtpPlot(psd_data,plot_type="mtp_all")
                # FFT
                elif self.decoder_type == 'fft':
                    psd_cuts = np.zeros((15,3,1024))
                    psd_data = np.zeros((3,1024))
                    for i in range(15):
                        psd_cuts[i,:,:] = self.hsd.fftSegment(y[:,i*1024:i*1024+1024])
                    for i in range(3):  # cut out the first segment to let the EEG signal settle after being turned on
                        psd_data[i,:] = np.mean(psd_cuts[1:,i,:],axis=0)
                # save the file
                np.savetxt(self.data_file_name, psd_data, fmt="%12.6G")
                break

        # TURN OFF THE MOBILAB AFTER RUN COMPLETE.
        self.device.stop()
        self.device.close()

# Run it!
decoder = HsdBaselineRemoval(COM_PORT=args.com_port,subject_id=args.subject_id,decoder_type=args.decoder_type)
print "Starting Baseline Removal Procedure - Don't Move! :)"
decoder.run()
print "All done."