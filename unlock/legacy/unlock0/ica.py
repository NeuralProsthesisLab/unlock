import numpy as np
import pylab as plt
import mdp

data = np.genfromtxt('/Users/bgalbraith/Dropbox/School/enobio data/12hz_test.txt',delimiter='\t')
x = data[0:2000, 1:4]
plt.figure()
for i in range(3):
    plt.subplot(311+i)
    plt.plot(x[:,i])

y = mdp.fastica(x)
plt.figure()
for i in range(3):
    plt.subplot(311+i)
    plt.plot(y[:,i])

plt.show()

