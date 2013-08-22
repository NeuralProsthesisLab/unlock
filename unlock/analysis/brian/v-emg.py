import numpy as np
from numpy import *
import matplotlib as plt
from matplotlib import *
import pylab
from pylab import *
import pandas as pd
from pandas import *

#acquiring data
f = open("bci_1.txt")
data = np.loadtxt(f)
ch1_a = data[:,0]
ch2_a = data[:,1]
ch3_a = data[:,2]
ref = data[:,8]

#initializing variables
past_location = 0

rightVisual = []
leftVisual = []
upVisual = []
downVisual = []

clue_1=1000
clue_2=-1000
left_location=0
past_left_location=0

clue_3=1000
clue_4=-1000
right_location=0
past_right_location=0

clue_5=-1000
clue_6=-1000
clue_7=-1000
up_location=0
past_up_location=0

clue_8=1000
clue_9=1000
clue_10=1000
down_location=0
past_down_location=0

BoxSize = 25
BoxSize2 = 200
BoxSize3 = 50

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

Qorder = "Start"

def lin_fit(signal):
    x = np.linspace(0,9999,num=10000)
    coefs = np.polyfit(x,signal[0:10000],1)
    fit = np.polyval(coefs,x)
    return signal[0:10000]-fit

for n in range(0,len(ch1_a)):#this loop is to mimic real-time acquisition
    ch1_b = np.append(ch1_b,ch1_a[n])
    ch2_b = np.append(ch2_b,ch2_a[n])
    ch3_b = np.append(ch3_b,ch3_a[n])

    if n==10000:
        ch1_c = copy(lin_fit(ch1_b))
        ch2_c = copy(lin_fit(ch2_b))
        ch3_c = copy(lin_fit(ch3_b))

        ch1_c[0:10000] = pd.rolling_mean(ch1_c[0:10000],BoxSize)
        ch2_c[0:10000] = pd.rolling_mean(ch2_c[0:10000],BoxSize)
        ch3_c[0:10000] = pd.rolling_mean(ch3_c[0:10000],BoxSize)

        ch1_c[0:10000] = pd.rolling_mean(ch1_c[0:10000],BoxSize2)
        ch2_c[0:10000] = pd.rolling_mean(ch2_c[0:10000],BoxSize2)
        ch3_c[0:10000] = pd.rolling_mean(ch3_c[0:10000],BoxSize2)

        ch1_c[0:10000] = pd.rolling_mean(ch1_c[0:10000],BoxSize2)
        ch2_c[0:10000] = pd.rolling_mean(ch2_c[0:10000],BoxSize2)
        ch3_c[0:10000] = pd.rolling_mean(ch3_c[0:10000],BoxSize2)

        ch1_c[0:10000] = pd.rolling_mean(ch1_c[0:10000],BoxSize2)
        ch2_c[0:10000] = pd.rolling_mean(ch2_c[0:10000],BoxSize2)
        ch3_c[0:10000] = pd.rolling_mean(ch3_c[0:10000],BoxSize2)

        ch1_c[0:10000] = pd.rolling_mean(ch1_c[0:10000],BoxSize3)
        ch2_c[0:10000] = pd.rolling_mean(ch2_c[0:10000],BoxSize3)
        ch3_c[0:10000] = pd.rolling_mean(ch3_c[0:10000],BoxSize3)

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

        fig1=figure()
        plot(diff(ch1_c[0:10000]))
        plot(diff(ch2_c[0:10000]))
        plot(diff(ch3_c[0:10000]))
        show()

        #the following is to set the thresholds for interpretation
        ch1_what = diff(copy(ch1_c[200:10000]))
        ch1_where = ch1_what[numpy.logical_not(numpy.isnan(ch1_what))]
        
        ch2_what = diff(copy(ch2_c[200:10000]))
        ch2_where = ch2_what[numpy.logical_not(numpy.isnan(ch2_what))]
        
        ch3_what = diff(copy(ch3_c[200:10000]))
        ch3_where = ch3_what[numpy.logical_not(numpy.isnan(ch3_what))]
        
        maxThresh = min([max(ch1_where),max(ch2_where),max(ch3_where)])*.40
        minThresh = max([min(ch1_where),min(ch2_where),min(ch3_where)])*.40
        
    if n>10000:
        x = np.linspace(n-9999,n,num=10000)

        coefs = np.polyfit(x,ch1_a[n-10000:n],1)
        ch1_c = np.append(ch1_c,ch1_a[n]-(n*coefs[0]+coefs[1]))
        coefs = np.polyfit(x,ch2_a[n-10000:n],1)
        ch2_c = np.append(ch2_c,ch2_a[n]-(n*coefs[0]+coefs[1]))
        coefs = np.polyfit(x,ch3_a[n-10000:n],1)
        ch3_c = np.append(ch3_c,ch3_a[n]-(n*coefs[0]+coefs[1]))      

        ch1_z = copy(ch1_c)
        ch2_z = copy(ch2_c)
        ch3_z = copy(ch3_c)
        ch1_z[n-1] = mean(ch1_z[n-BoxSize:])
        ch2_z[n-1] = mean(ch2_z[n-BoxSize:])
        ch3_z[n-1] = mean(ch3_z[n-BoxSize:])
        ch1_m = np.append(ch1_m,ch1_z[n-1])
        ch2_m = np.append(ch2_m,ch2_z[n-1])
        ch3_m = np.append(ch3_m,ch3_z[n-1])

        ch1_z = copy(ch1_m)
        ch2_z = copy(ch2_m)
        ch3_z = copy(ch3_m)
        ch1_z[n-1] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n-1] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n-1] = mean(ch3_z[n-BoxSize2:])
        ch1_n = np.append(ch1_n,ch1_z[n-1])
        ch2_n = np.append(ch2_n,ch2_z[n-1])
        ch3_n = np.append(ch3_n,ch3_z[n-1])

        ch1_z = copy(ch1_n)
        ch2_z = copy(ch2_n)
        ch3_z = copy(ch3_n)
        ch1_z[n-1] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n-1] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n-1] = mean(ch3_z[n-BoxSize2:])
        ch1_o = np.append(ch1_o,ch1_z[n-1])
        ch2_o = np.append(ch2_o,ch2_z[n-1])
        ch3_o = np.append(ch3_o,ch3_z[n-1])

        ch1_z = copy(ch1_o)
        ch2_z = copy(ch2_o)
        ch3_z = copy(ch3_o)
        ch1_z[n-1] = mean(ch1_z[n-BoxSize2:])
        ch2_z[n-1] = mean(ch2_z[n-BoxSize2:])
        ch3_z[n-1] = mean(ch3_z[n-BoxSize2:])
        ch1_p = np.append(ch1_p,ch1_z[n-1])
        ch2_p = np.append(ch2_p,ch2_z[n-1])
        ch3_p = np.append(ch3_p,ch3_z[n-1])

        ch1_z = copy(ch1_p)
        ch2_z = copy(ch2_p)
        ch3_z = copy(ch3_p)
        ch1_z[n-1] = mean(ch1_z[n-BoxSize3:])
        ch2_z[n-1] = mean(ch2_z[n-BoxSize3:])
        ch3_z[n-1] = mean(ch3_z[n-BoxSize3:])
        ch1_y = np.append(ch1_y,ch1_z[n-1])
        ch2_y = np.append(ch2_y,ch2_z[n-1])
        ch3_y = np.append(ch3_y,ch3_z[n-1])

        ch1_X=diff(ch1_y)
        ch2_X=diff(ch2_y)
        ch3_X=diff(ch3_y)
        
#The Following If Statements Are Detecting Peaks
    #Left
        if ch1_X[n-4]<ch1_X[n-3] and ch1_X[n-3]>ch3_X[n-2] and ch1_X[n-3]>maxThresh:
            clue_1 = n

        if ch3_X[n-4]>ch3_X[n-3] and ch3_X[n-3]<ch3_X[n-2] and ch3_X[n-3]<minThresh:
            clue_2 = n

        if abs(diff([clue_1,clue_2]))<100:
            left_location = (clue_1+clue_2)/2
            
        if past_left_location == 0 and clue_1!=1000 and clue_2!=-1000:
            past_left_location = n
            
        if (left_location-past_location)>500:
            print('Left', left_location)
            past_location = left_location
            past_left_location = left_location
            leftVisual.append(left_location)
            clue_1=1000
            clue_2=-1000
    #Right
        if ch3_X[n-4]<ch3_X[n-3] and ch3_X[n-3]>ch3_X[n-2] and ch3_X[n-3]>maxThresh:
            clue_3 = n

        if ch1_X[n-4]>ch1_X[n-3] and ch1_X[n-3]<ch1_X[n-2] and ch1_X[n-3]<minThresh:
            clue_4 = n

        if abs(diff([clue_3,clue_4]))<100:
            right_location = (clue_3+clue_4)/2
            
        if past_right_location == 0 and clue_3!=1000 and clue_4!=-1000:
            past_right_location = n
            
        if (right_location-past_location)>500:
            print('Right', right_location)
            past_location = right_location
            past_right_location = right_location
            rightVisual.append(right_location)
            clue_3=1000
            clue_4=-1000
    #Up
        if ch1_X[n-4]<ch1_X[n-3] and ch1_X[n-3]>ch1_X[n-2] and ch1_X[n-3]>maxThresh:
            clue_5 = n

        if ch2_X[n-4]<ch2_X[n-3] and ch2_X[n-3]>ch2_X[n-2] and ch2_X[n-3]>maxThresh:
            clue_6 = n

        if ch3_X[n-4]<ch3_X[n-3] and ch3_X[n-3]>ch3_X[n-2] and ch3_X[n-3]>maxThresh:
            clue_7 = n

        if abs(diff([clue_5,clue_6]))<100 and abs(diff([clue_5,clue_7]))<100 and abs(diff([clue_6,clue_7]))<100:
            up_location = (clue_5+clue_6+clue_7)/3
            
        if past_up_location == 0 and clue_5!=-1000 and clue_6!=-1000 and clue_7!=-1000:
            past_up_location = n
            
        if (up_location-past_location)>500:
            print('Up', up_location)
            past_location = up_location
            past_up_location = up_location
            upVisual.append(up_location)
            clue_5 = -1000
            clue_6 = -1000
            clue_7 = -1000
    #Down
        if ch1_X[n-4]>ch1_X[n-3] and ch1_X[n-3]<ch1_X[n-2] and ch1_X[n-3]<minThresh:
            clue_8 = n

        if ch2_X[n-4]>ch2_X[n-3] and ch2_X[n-3]<ch2_X[n-2] and ch2_X[n-3]<minThresh:
            clue_9 = n

        if ch3_X[n-4]>ch3_X[n-3] and ch3_X[n-3]<ch3_X[n-2] and ch3_X[n-3]<minThresh:
            clue_10 = n

        if abs(diff([clue_8,clue_9]))<100 and abs(diff([clue_8,clue_10]))<100 and abs(diff([clue_9,clue_10]))<100:
            down_location = (clue_8+clue_9+clue_10)/3
            
        if past_down_location == 0 and clue_5!=1000 and clue_6!=1000 and clue_7!=1000:
            past_down_location = n
            
        if (down_location-past_location)>500:
            print('Down', down_location)
            past_location = down_location
            past_down_location = down_location
            downVisual.append(down_location)
            clue_8 = 1000
            clue_9 = 1000
            clue_10 = 1000



            
fig1 = plt.figure()
p1 = plot(ch1_y, label='ch1')
p2 = plot(ch2_y, label='ch2')
p3 = plot(ch3_y, label='ch3')
plt.title("Filtered Signal")    
legend()
fig2 = plt.figure()
plot(ch1_X, label='ch1')
plot(ch2_X, label='ch2')
plot(ch3_X, label='ch3')
plot(upVisual,zeros(len(upVisual)),'ro',label='Up')
plot(downVisual,zeros(len(downVisual)),'bo',label='Down')
plot(rightVisual,zeros(len(rightVisual)),'g^',label='Left')
plot(leftVisual,zeros(len(leftVisual)),'bs',label='Right')
plt.title("Difference")
legend()
show()
