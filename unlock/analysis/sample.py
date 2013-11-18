import argparse
import os
import numpy
from matplotlib.pyplot import *

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('inputFile')
    argParser.add_argument('-export', dest='exportPath', default=False)
    args = argParser.parse_args()
    
    fin = open(args.inputFile, 'r')
    t,y = [],[]
    next(fin) # Ignore first line (which is usually column names) in csv
    for line in fin:
        pair = line.split(',')
        t.append(float(pair[1]))
        y.append(float(pair[2]))
    fin.close()
    
    a,b = numpy.polyfit(t,y,1)
    approximate = [a*t1 + b for t1 in t]
    
    plot(t,y,'.')
    plot(t,approximate)
    
    if (args.exportPath):
        savefig(args.exportPath)
    else:
        show()