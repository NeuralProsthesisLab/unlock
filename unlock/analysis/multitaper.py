import argparse
import numpy as np
import matplotlib.pyplot as plt
from nitime.viz import winspect

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

fig01 = plt.figure()
winspect(signal, fig01)
plt.show()