import argparse
import numpy as np
import matplotlib.pyplot as plt

argParser = argparse.ArgumentParser()
argParser.add_argument('datafile')
argParser.add_argument('--fromtime', type=float, default=0)
argParser.add_argument('--totime', type=float, default=None)
args = argParser.parse_args()

time,signal = [],[]
fin = open(args.datafile, 'r')
for line in fin:
    words = line.split(',')
    time_value = float(words[1])
    signal_value = float(words[0])
    
    if (time_value > args.fromtime and (args.totime == None or time_value < args.totime)):
        time.append(time_value)
        signal.append(signal_value)
fin.close()
time,signal = np.array(time),np.array(signal)

fft = np.fft.fft(signal)
sampleSpacing = time[-1] / time.size

freq = np.fft.fftfreq(signal.size, sampleSpacing)
power = 10*np.log10(np.abs(fft)**2)

plt.plot(freq, power)
plt.ylabel('Power (dB)')
plt.xlabel('Frequency (Hz)')
plt.show()