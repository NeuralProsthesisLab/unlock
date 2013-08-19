import numpy as np
from numpy import *

import matplotlib as plt
from matplotlib import *

import pylab
from pylab import *

f = open("bci_4.txt")
data = np.loadtxt(f)
ch1 = data[:,0]
ch2 = data[:,1]
ch3 = data[:,2]
ref = data[:,8]

sampNo = linspace(0,len(ch1)-1,num=len(ch1))

plot(sampNo,ch1,sampNo,ch2,sampNo,ch3)
show()


