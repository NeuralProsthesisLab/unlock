import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

# Parse arguments
argParser = argparse.ArgumentParser()
argParser.add_argument('inputFile')
args = argParser.parse_args()

# Input signal: Array of 256 quadruples
input = []
fin = open(args.inputFile, 'r')
for line in fin:
    quad = line.split(',')
    input.append([float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3])]);
fin.close()
signal = np.array(input)

# Get 2 dimensional discrete fourier transform
sp = np.fft.fft2(signal)
amp = np.abs(sp)
freq = np.fft.fftfreq(signal.shape[0])

# Plot amplitude vs frequency
plt.figure(1)
plt.plot(freq, amp)
plt.xlabel('Frequency')
plt.ylabel('Amplitude')

# Plot spectrogram
plt.figure(2)
plt.specgram(signal, NFFT=1024)
plt.xlabel("Time")
plt.ylabel('Frequency')

plt.show()