import numpy as np

fh = open('/Users/bgalbraith/Desktop/hsd_15hz.txt')
data = fh.readlines()
fh.close()

samples = np.zeros((5,len(data)))
for i,d in enumerate(data):
    samples[:,i] = map(int,d.split('\t')[0:5])

print (samples,0)

