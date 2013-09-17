# a,b,c,d = specgram(x, NFFT=2048, Fs=500, noverlap=0)
# imshow(a[41:90,:], aspect='auto', origin='lower',extent=[0,8,10.00,21.73], interpolation='nearest')

import numpy as np
import mdp
import pylab as plt

data = np.genfromtxt('/Users/bgalbraith/Dropbox/School/enobio data/12hz_test.txt',delimiter='\t')
x = data[4000:8000,0:7]
plt.figure()
plt.subplot(311)
plt.plot(x-np.mean(x,axis=0))
#x = sig.detrend(x, axis=0)
#x -= np.mean(x, axis=0)
#x -= np.mean(x, axis=1).reshape((2000,1))
#x -= x[:,6].reshape((x.shape[0],1))
x = mdp.fastica(x)
plt.subplot(312)
plt.plot(x)
y = np.abs(np.fft.rfft(x, n=2048, axis=0))
f = np.abs(np.fft.fftfreq(2048, d=0.002)[0:1025])
plt.subplot(313)
plt.plot(f,y)
plt.legend(['PO7','O1','Oz','O2','PO8','P3','Pz','P4'])
#x -= data[:,6].reshape((x.shape[0],1))
#x -= np.mean(x, axis=0)
#x -= x[:,6].reshape((x.shape[0],1))
#plt.plot(x)
#x = data[:,[2,6]]
#x = data[:,0] - data[:,1]
#x -= np.mean(x,axis=0)
#x = sig.detrend(data[:,2])
#x = data[:,2] - data[:,6]
#x = sig.detrend(x)
# mu = x[0,:]
# y = np.zeros(x.shape)
# for i in xrange(y.shape[0]):
#     mu = 0.95*mu + 0.05*x[i,:]
#     y[i,:] = x[i,:] - mu
# plt.plot(y[:,2])
#q = *x#(x-np.mean(x,axis=0))
#q = x[:,1:4]-x[:,5:8]
#q -= np.mean(q,axis=0)
#q = y[:]
#q *= np.hanning(2000).reshape((2000,1))
# z = np.abs(np.fft.fft(q,2048,axis=0))
# f = np.arange(0,250,500/2048.0)
# t = np.arange(0,4,1/500.0)
# plt.subplot(211)
# plt.plot(f,z[0:len(f),:])
# plt.xlim([11,16])
# plt.ylim([0,3e5])
# plt.subplot(212)
# plt.plot(t,q)

nfft = 2048
fstep = 500.0/nfft
lb = int(11/fstep)
ub = int(16/fstep)
plt.figure()
full = np.zeros((20,7))
for i in range(7):
    #plt.subplot(241+i)
    a,b,c,d = plt.specgram(x[:,i],NFFT=nfft, Fs=500, noverlap=0)
    full[:,i] = a[lb:ub,:].T
    #plt.imshow(a[lb:ub,:], aspect='auto', origin='lower',extent=[0,1,b[lb],b[ub]], interpolation='nearest')
#plt.figure()
plt.imshow(full, aspect='auto', origin='lower',extent=[0,8,b[lb],b[ub]], interpolation='nearest',cmap=plt.cm.bone_r)
plt.colorbar()
#a,b,c,d = plt.specgram(y[:,2],NFFT=2048,Fs=500)
#a,b,c,d = plt.specgram(y[:,3]-y[:,7],NFFT=2048,Fs=500)
plt.show()