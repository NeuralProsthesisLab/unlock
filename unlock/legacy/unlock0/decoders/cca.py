# CANONICAL CORRELATION ANALYSIS: Based on Magnus Borga's Matlab code here:
# http://www.imt.liu.se/~magnus/cca/
# Number of variables (not observations) for X and Y, thus column numbers MUST be
# equal and only rows can vary between X and Y! Assumes columns=samples. 

import numpy as np
import scipy.signal as sigfilt

class CCA():
    def __init__(self, fs,tSecs,lpass,hpass):
        lfft            = fs*tSecs            # signal length
        self.nfft       = self.nextpow2(lfft) # FFT next power of 2 length
        [self.b,self.a] = sigfilt.butter(4,np.divide([lpass,hpass],fs/2),btype='bandpass')
        self.f          = fs/2*np.linspace(0,1,self.nfft/2+1) # frequency linspace

    def nextpow2(self,i):
        n = 2
        while n < i: n = n * 2
        return n

    def preproc(self, sig):
        X = sig - np.mean(sig) # Zero-mean raw data
        X = sigfilt.lfilter(b,a,X)  # Butterworth filter z-m data

        return X

    def cca(self,X,Y):
    
        # Get X and Y sizes. Tests to make sure they have the same number of samples.
        sx = np.shape(X)[0]
        sy = np.shape(Y)[0]
        sxSampNum = np.shape(X)[1]
        sySampNum = np.shape(Y)[1]
        if sxSampNum != sySampNum:
            print """\n\nWarning! Your X and Y samples are different lengths!
                      Prepare for error message.\n\n"""

        # 1) Calculate covariance matrices
        z = np.concatenate((X,Y),axis=0)
        C = np.cov(z)
        Cxx = C[0:sx,0:sx] + (10**(-8))*np.eye(sx)
        Cxy = C[0:sx,sx:sx+sy]
        Cyx = Cxy.conj().transpose()
        Cyy = C[sx:sx+sy,sx:sx+sy] + (10**(-8))*np.eye(sy)
        invCyy = np.linalg.inv(Cyy)

        # 2) Calculate Wx and r
        r,Wx = np.linalg.eig(np.dot(np.linalg.inv(Cxx),np.dot(np.dot(Cxy,invCyy),Cyx))) # Basis in X
        r = np.sqrt(np.real(r)) # Canonical correlations

        # 3) Sort correlations
        V = np.fliplr(Wx)   # reverse order of eigenvectors
        r = np.flipud(r)    # extract eigenvalues and reverse their order
        r = (np.real(r))    # only use real eigenvalues
        I = r.argsort()     # return eigenvalue array of indices
        r = np.sort(r)      # sort reversed eigenvalues in ascending order
        r = np.flipud(r)    # restore sorted eigenvalues into descending order
        for j in range(len(I)):
            Wx[:,j] = V[:,I[j]]  # sort reversed eigenvectors in ascending order
        Wx = np.fliplr(Wx)	# restore sorted eigenvectors into descending order

        # 4) Calculate Wy
        Wy = np.dot(np.dot(invCyy,Cyx),Wx)                   # Basis in Y
        Wy = Wy/np.tile(np.sqrt(np.sum(abs(Wy)**2,axis=0)),(sy,1)) # Normalize Wy

        # Function outputs
        return [Wx, Wy, r]
