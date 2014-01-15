import argparse
import numpy as np
import matplotlib.pyplot as plt

argParser = argparse.ArgumentParser()
argParser.add_argument('datafile')
args = argParser.parse_args()

time,signal = [],[]
fin = open(args.datafile, 'r')
for line in fin:
    words = line.split(',')
    time.append(float(words[1]))
    signal.append(float(words[0]))
fin.close()
time,signal = np.array(time),np.array(signal)

samplingRate = time.size / time[-1]

plt.specgram(signal, Fs=samplingRate)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar().set_label('Amplitude (Frequency power)')
plt.show()