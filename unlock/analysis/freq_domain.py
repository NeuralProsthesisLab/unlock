import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

# Parse arguments
argParser = argparse.ArgumentParser()
argParser.add_argument('inputFile')
args = argParser.parse_args()

# Input signal: 256 quadruples
input = []
fin = open(args.inputFile, 'r')
for line in fin:
    quad = line.split(',')
    input.append([float(quad[0]), float(quad[1]), float(quad[2]), float(quad[3])]);
fin.close()
signal = np.array(input)

# Get FFT for freq domain plot
sp = np.fft.fft(signal)
freq = np.fft.fftfreq(signal.shape[0])

# Plot signal in frequency domain
plt.figure(1)
plt.plot(freq, sp.real, freq, sp.imag)

# Plot spectrogram
plt.figure(2)
plt.specgram(signal, NFFT=1024)

plt.show()