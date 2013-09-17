
#===============================================================================
# Online Canonical Correlation Analysis (CCA) Decoder
#===============================================================================

# LIBRARY IMPORTS
import cca
import pygtec
import acquire

import socket
import numpy as np
import scipy.signal as sigfilt
from scipy.io import loadmat

# UDP SETTINGS
UDP_IP = 'localhost'
UDP_PORT=33445
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# GTEC SETTINGS
device = pygtec.MOBIlab()
device.open("COM3")
device.init(112,0)
device.start()
nElecs = 3   # Number of electrodes used
nFrames = 8  # Number of frames grabbed during acquire (per electrode)
nGtecSamps = nElecs*nFrames

# CLASSIFIER SETTINGS
fs     = 256.0     # Sampling rate
tSecs  = 2.0       # Number of trial seconds before HSD prediction
lpass  = 10.0      # Low end of filter
hpass  = 34.0      # High end of filter
tLen   = int(fs*tSecs) # Number of decoded trial samples
[b,a] = sigfilt.butter(4,np.divide([lpass,hpass],fs/2),btype='bandpass')
nAcqIters = int((fs*nElecs*tSecs)/nGtecSamps)

# LOAD CCA Y TEMPLATES
Y = loadmat('ccaTemplate.mat')
Yu=Y['Yu']; Yd=Y['Yd']; Yl=Y['Yl']; Yr=Y['Yr']

# START THE ONLINE CCA DECODER!
while True:
   
    # STEP 1: Get data from gTec amp; add to buffer.
    sig = acquire.gtecBuffer(device,tLen,nAcqIters,nElecs,nGtecSamps,nFrames)

    # STEP 2: Zero-mean and filter signal segment.
    X = np.zeros((nElecs,tLen))
    for j in range(nElecs):             # Repeat for each electrode:
        X[j,:] = sig[j,:] - np.mean(sig[j,:]) # Zero-mean raw data
        X[j,:] = sigfilt.lfilter(b,a,X[j,:])  # Butterworth filter z-m data
    
    # STEP 3: CCA
    Wx,Wy,Ru = cca.cca(X,Yu)
    Wx,Wy,Rd = cca.cca(X,Yd)
    Wx,Wy,Rl = cca.cca(X,Yl)
    Wx,Wy,Rr = cca.cca(X,Yr)
    allR     = [Ru[0],Rd[0],Rl[0],Rr[0]]
    ccaWinner = np.argsort(allR)[3]+1
    print '\n\nPredicted winner is: ', ccaWinner
    sock.sendto(str(ccaWinner),(UDP_IP,UDP_PORT))

# TURN OFF THE MOBILAB AFTER RUN COMPLETE.
device.stop()
device.close()
sock.close()