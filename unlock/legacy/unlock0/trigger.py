import socket
import time
import numpy as np

sock = socket.socket(type=socket.SOCK_DGRAM)
sock.settimeout(0.001)
sock.bind(('127.0.0.1',33448))

tic = 0
toc = time.time()
i = 0
x = np.zeros(50)
while i <= 50:
    try:
        trigger, _ = sock.recvfrom(1)
        trigger = int(trigger)
        tic = toc
        toc = time.time()
        dt = toc - tic
        if i > 0:
            x[i-1] = dt
        i += 1
    except socket.timeout:
        pass
    except socket.error:
        pass
    except ValueError:
        pass

sock.close()
print x.mean(), x.std()