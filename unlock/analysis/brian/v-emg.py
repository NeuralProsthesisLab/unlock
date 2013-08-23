import numpy as np
from numpy import *
import matplotlib as plt
from matplotlib import *
import pylab
from pylab import *
import pandas as pd
from pandas import *

#acquiring data
f = open("bci_11_90.txt")
data = np.loadtxt(f)
ch1 = data[:,0] #AF7
ch2 = data[:,6] #FPz
ch3 = data[:,2] #AF8

#variables to tweak
pkDist = 200 #peaks must be >= pkDist samples from the last recorded peak to be detected
pkProx = 100 #peaks between channels must be <= pkProx samples away from each other to be interpreted as a single event
initSamp = 6000 #initial sample size used to determine thresholds
linLen = 5000 #number of samples from current to linearize against. NOTE: must be <= initSamp
BoxSize = 25
BoxSize2 = 200
BoxSize3 = 50
maxThresh_percent = .4
minThresh_percent = .4

#initializing variables (placeholders)
history = ['history',':']
past_loc = 0
t1Visual = []
t2Visual = []
t3Visual = []
t4Visual = []
clue_1 = 1000
clue_2 = -1000
t1_loc = 0
past_t1_loc = 0
clue_3 = 1000
clue_4 = -1000
t2_loc = 0
past_t2_loc = 0
clue_5 = -1000
clue_6 = -1000
clue_7 = -1000
t3_loc = 0
past_t3_loc = 0
clue_8 = 1000
clue_9 = 1000
clue_10 = 1000
t4_loc = 0
past_t4_loc = 0
ch1_b = np.array([])
ch2_b = np.array([])
ch3_b = np.array([])
ch1_c = np.array([])
ch2_c = np.array([])
ch3_c = np.array([])
countD = 0
countU = 0
countR = 0
countL = 0

def lin_fit(signal):
    x = np.arange(len(signal))
    coefs = np.polyfit(x,signal,1)
    fit = np.polyval(coefs,x)
    return signal - fit

for n in range(0, len(ch1)):#this loop is to mimic real-time acquisition
    ch1_b = np.append(ch1_b,ch1[n])
    ch2_b = np.append(ch2_b,ch2[n])
    ch3_b = np.append(ch3_b,ch3[n])

    if n == initSamp:
        ch1_c = copy(lin_fit(ch1_b))
        ch2_c = copy(lin_fit(ch2_b))
        ch3_c = copy(lin_fit(ch3_b))
        for i in range(0,4):
            ch1_c = pd.rolling_mean(ch1_c, BoxSize)
            ch2_c = pd.rolling_mean(ch2_c, BoxSize)
            ch3_c = pd.rolling_mean(ch3_c, BoxSize)
        for i in range(0,4):
            ch1_c = pd.rolling_mean(ch1_c, BoxSize2)
            ch2_c = pd.rolling_mean(ch2_c, BoxSize2)
            ch3_c = pd.rolling_mean(ch3_c, BoxSize2)
        for i in range(0,4):
            ch1_c = pd.rolling_mean(ch1_c, BoxSize3)
            ch2_c = pd.rolling_mean(ch2_c, BoxSize3)
            ch3_c = pd.rolling_mean(ch3_c, BoxSize3)

        ch1_y = copy(ch1_c)
        ch2_y = copy(ch2_c)
        ch3_y = copy(ch3_c)
        ch1_m = copy(ch1_c)
        ch2_m = copy(ch2_c)
        ch3_m = copy(ch3_c)
        ch1_n = copy(ch1_c)
        ch2_n = copy(ch2_c)
        ch3_n = copy(ch3_c)
        ch1_o = copy(ch1_c)
        ch2_o = copy(ch2_c)
        ch3_o = copy(ch3_c)
        ch1_p = copy(ch1_c)
        ch2_p = copy(ch2_c)
        ch3_p = copy(ch3_c)

        #fig1 = figure()
        #plot(diff(ch1_c))
        #plot(diff(ch2_c))
        #plot(diff(ch3_c))
        #show()

        #the following is to set the thresholds for interpretation
        ch1_thresh_1 = diff(copy(ch1_c))
        ch1_thresh_2 = ch1_thresh_1[numpy.logical_not(numpy.isnan(ch1_thresh_1))]
        ch2_thresh_1 = diff(copy(ch2_c))
        ch2_thresh_2 = ch2_thresh_1[numpy.logical_not(numpy.isnan(ch2_thresh_1))]
        ch3_thresh_1 = diff(copy(ch3_c))
        ch3_thresh_2 = ch3_thresh_1[numpy.logical_not(numpy.isnan(ch3_thresh_1))]
        maxThresh = min([max(ch1_thresh_2),max(ch2_thresh_2), max(ch3_thresh_2)])*maxThresh_percent
        minThresh = max([min(ch1_thresh_2),min(ch2_thresh_2), min(ch3_thresh_2)])*minThresh_percent
        print('Max Threshold:', maxThresh)
        print('Min Threshold:', minThresh)

    if n > initSamp:

        #Each new sample is linearized before appended
        x = np.arange(n-linLen, n)
        coefs = np.polyfit(x, ch1_b[n-linLen:n], 1)
        ch1_c = np.append(ch1_c, ch1_b[n]-(n*coefs[0]+coefs[1]))
        coefs = np.polyfit(x, ch2_b[n-linLen:n], 1)
        ch2_c = np.append(ch2_c, ch2_b[n]-(n*coefs[0]+coefs[1]))
        coefs = np.polyfit(x,ch3_b[n-linLen:n], 1)
        ch3_c = np.append(ch3_c, ch3_b[n]-(n*coefs[0]+coefs[1]))

        #Each new sample undergoes boxcar filtering
        ch1_z = copy(ch1_c)
        ch2_z = copy(ch2_c)
        ch3_z = copy(ch3_c)
        ch1_z[n] = mean(ch1_z[n-BoxSize:])
        ch2_z[n] = mean(ch2_z[n-BoxSize:])
        ch3_z[n] = mean(ch3_z[n-BoxSize:])
        ch1_m = np.append(ch1_m,ch1_z[n])
        ch2_m = np.append(ch2_m,ch2_z[n])
        ch3_m = np.append(ch3_m,ch3_z[n])
        ch1_z = copy(ch1_m)
        ch2_z = copy(ch2_m)
        ch3_z = copy(ch3_m)
        ch1_z[n] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n] = mean(ch3_z[n-BoxSize2:])
        ch1_n = np.append(ch1_n, ch1_z[n])
        ch2_n = np.append(ch2_n, ch2_z[n])
        ch3_n = np.append(ch3_n, ch3_z[n])
        ch1_z = copy(ch1_n)
        ch2_z = copy(ch2_n)
        ch3_z = copy(ch3_n)
        ch1_z[n] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n] = mean(ch3_z[n-BoxSize2:])
        ch1_o = np.append(ch1_o, ch1_z[n])
        ch2_o = np.append(ch2_o, ch2_z[n])
        ch3_o = np.append(ch3_o, ch3_z[n])
        ch1_z = copy(ch1_o)
        ch2_z = copy(ch2_o)
        ch3_z = copy(ch3_o)
        ch1_z[n] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n] = mean(ch3_z[n-BoxSize2:])
        ch1_p = np.append(ch1_p, ch1_z[n])
        ch2_p = np.append(ch2_p, ch2_z[n])
        ch3_p = np.append(ch3_p, ch3_z[n])
        ch1_z = copy(ch1_p)
        ch2_z = copy(ch2_p)
        ch3_z = copy(ch3_p)
        ch1_z[n] = mean(ch1_z[n-BoxSize3:])
        ch2_z[n] = mean(ch2_z[n-BoxSize3:])
        ch3_z[n] = mean(ch3_z[n-BoxSize3:])
        ch1_y = np.append(ch1_y, ch1_z[n])
        ch2_y = np.append(ch2_y, ch2_z[n])
        ch3_y = np.append(ch3_y, ch3_z[n])

        ch1_X = diff(ch1_y)
        ch2_X = diff(ch2_y)
        ch3_X = diff(ch3_y)

#The Following If Statements Are Detecting Peaks-----------------------------------------------------------------------

    #Type 1 (AF7 max, AF8 min)-------------------------------------------------------------
        if ch1_X[n-4] < ch1_X[n-3] and ch1_X[n-3] > ch3_X[n-2] and ch1_X[n-3] > maxThresh:
            clue_1 = n
        if ch3_X[n-4] > ch3_X[n-3] and ch3_X[n-3] < ch3_X[n-2] and ch3_X[n-3] < minThresh:
            clue_2 = n
        if abs(diff([clue_1,clue_2])) < pkProx:
            t1_loc = mean([clue_1, clue_2])
        if past_t1_loc == 0 and clue_1 != 1000 and clue_2 != -1000:
            past_t1_loc = n
        if (t1_loc - past_loc) > pkDist:
            past_loc = t1_loc
            past_t1_loc = t1_loc
            t1Visual.append(t1_loc)
            history.append('t1')
            clue_1 = 1000
            clue_2 = -1000
            #print('Type 1', t1_loc)
            #print(history)

    #Type 2 (AF7 min, AF8 max)--------------------------------------------------------------
        if ch3_X[n-4] < ch3_X[n-3] and ch3_X[n-3] > ch3_X[n-2] and ch3_X[n-3] > maxThresh:
            clue_3 = n
        if ch1_X[n-4] > ch1_X[n-3] and ch1_X[n-3] < ch1_X[n-2] and ch1_X[n-3] < minThresh:
            clue_4 = n
        if abs(diff([clue_3, clue_4])) < pkProx:
            t2_loc = mean([clue_3, clue_4])
        if past_t2_loc == 0 and clue_3 != 1000 and clue_4 != -1000:
            past_t2_loc = n
        if (t2_loc - past_loc) > pkDist:
            past_loc = t2_loc
            past_t2_loc = t2_loc
            t2Visual.append(t2_loc)
            history.append('t2')
            clue_3 = 1000
            clue_4 = -1000
            #print('Type 2', t2_loc)
            #print(history)

    #Type 3 (AF7 max, FPz max, AF8 max)-----------------------------------------------------
        if ch1_X[n-4] < ch1_X[n-3] and ch1_X[n-3] > ch1_X[n-2] and ch1_X[n-3] > maxThresh:
            clue_5 = n
        if ch2_X[n-4] < ch2_X[n-3] and ch2_X[n-3] > ch2_X[n-2] and ch2_X[n-3] > maxThresh:
            clue_6 = n
        if ch3_X[n-4] < ch3_X[n-3] and ch3_X[n-3] > ch3_X[n-2] and ch3_X[n-3] > maxThresh:
            clue_7 = n
        if abs(diff([clue_5, clue_6])) < pkProx and abs(diff([clue_5, clue_7])) < pkProx and abs(diff([clue_6, clue_7])) < pkProx:
            t3_loc = mean([clue_5, clue_6, clue_7])
        if past_t3_loc == 0 and clue_5 != -1000 and clue_6 != -1000 and clue_7 != -1000:
            past_t3_loc = n
        if (t3_loc - past_loc) > pkDist:
            past_loc = t3_loc
            past_t3_loc = t3_loc
            history.append('t3')
            clue_5 = -1000
            clue_6 = -1000
            clue_7 = -1000
            t3Visual.append(t3_loc) #for visualization only (not needed in final code)
            #print(history)
            #print('Type 3', t3_loc)

    #Type 4 (AF7 min, FPz min, AF8 min)------------------------------------------------------
        if ch1_X[n-4] > ch1_X[n-3] and ch1_X[n-3] < ch1_X[n-2] and ch1_X[n-3] < minThresh:
            clue_8 = n
        if ch2_X[n-4] > ch2_X[n-3] and ch2_X[n-3] < ch2_X[n-2] and ch2_X[n-3] < minThresh:
            clue_9 = n
        if ch3_X[n-4] > ch3_X[n-3] and ch3_X[n-3] < ch3_X[n-2] and ch3_X[n-3] < minThresh:
            clue_10 = n
        if abs(diff([clue_8, clue_9])) < pkProx and abs(diff([clue_8, clue_10])) < pkProx and abs(diff([clue_9, clue_10])) < pkProx:
            t4_loc = mean([clue_8, clue_9, clue_10])
        if past_t4_loc == 0 and clue_5 != 1000 and clue_6 != 1000 and clue_7 != 1000:
            past_t4_loc = n
        if (t4_loc - past_loc) > pkDist:
            past_loc = t4_loc
            past_t4_loc = t4_loc
            history.append('t4')
            clue_8 = 1000
            clue_9 = 1000
            clue_10 = 1000
            t4Visual.append(t4_loc) #for visualization only (not needed in final code)
            #print('Type 4', t4_loc)
            #print(history)

    #Below would be the controls on the cursor:------------------------------------------------------------------------
        if history[-1] == 't1' and history[-2] == 't2':
            history.append('left')
        if history[-1] == 't2' and history[-2] == 't1':
            history.append('right')
        if history[-1] == 't3' and history[-2] == 't4':
            history.append('up')
        if history[-1] == 't4' and history[-2] == 't3':
            history.append('down')
        if history[-1] == 't3' and history[-2] == 't3' and history[-3] == 't3':
            history.append('Error: return to last position')

#the following is for visualization purposes only----------------------------------------------------------------------
fig1 = plt.figure()
p1 = plot(ch1_y, label='AF7')
p2 = plot(ch2_y, label='FPz')
p3 = plot(ch3_y, label='AF8')
plt.title("Filtered Signal")
legend()
fig2 = plt.figure()
plot(ch1_X, label='AF7')
plot(ch2_X, label='FPz')
plot(ch3_X, label='AF8')
plot(t3Visual,zeros(len(t3Visual)), 'ro', label='Type 3')
plot(t4Visual,zeros(len(t4Visual)), 'bo', label='Type 4')
plot(t2Visual,zeros(len(t2Visual)), 'g^', label='Type 2')
plot(t1Visual,zeros(len(t1Visual)), 'bs', label='Type 1')
plt.title("Difference")
legend()
show()
