import socket
import time
import json
import numpy as np

sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock3.settimeout(0.001)

#data = np.load("data_sweep_BG030612.npy")

data = np.genfromtxt('/Users/bgalbraith/Desktop/enobio_13hz.txt',delimiter='\t')
for row in data:
    print row[1:4]
    s = json.dumps(row[[1,2,3,5,6,7]].tolist())
    sock3.sendto(s,('127.0.0.1',33447))
    time.sleep(1.0/500.0)