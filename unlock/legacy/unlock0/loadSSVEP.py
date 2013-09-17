import socket
from fileparser import fileParser
import time
import json
import numpy as np

sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock3.settimeout(0.001)

dec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dec_sock.settimeout(0.001)

data        = fileParser("udlr_runData_SSVEP-H-014_1348.txt")
y           = np.transpose(data[:,3:6])
n_trials    = int(data[-1,0])

for row in data:
    s = json.dumps(row[3:6].tolist())
    sock3.sendto(s,('127.0.0.1',33447))

    d = json.dumps(row[2].tolist())
    dec_sock.sendto(d,('127.0.0.1',33448))

    time.sleep(1.0/256.0)

