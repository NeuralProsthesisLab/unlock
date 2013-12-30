import argparse

import numpy as np
import matplotlib.pyplot as plt


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataFilePath')
    args = parser.parse_args()
    
    return args.dataFilePath
    
def _read_and_format_data(dataFilePath):
    time = []
    signal = []

    fin = open(dataFilePath, 'r')
    for line in fin:
        values = line.split(',')
        time.append(float(values[1]))
        signal.append(float(values[0]))
    fin.close()
    
    time = np.array(time)
    signal = np.array(signal)
    
    return time,signal
    
def _analyze(time, signal):
    sampleSpacing = time[-1] / time.size
    freqs = np.fft.fftfreq(time.size, d=sampleSpacing)
    fft = np.fft.fft(signal)
    amps = np.abs(fft)
    
    plt.plot(freqs, amps)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.show()
    
    
if __name__ == '__main__':
    dataFilePath = _parse_args()
    time,signal = _read_and_format_data(dataFilePath)
    _analyze(time,signal)