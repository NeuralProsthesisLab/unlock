import socket
import threading

class MalformedResponseError(Exception):
    pass

class StreamClient:
    def __init__(self, host, port, timeout=0.1, debug=False):
        self.timeout = timeout
        self.sock = socket.socket(type=socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        self.hostaddr = (socket.gethostbyname(host), port)
        self.streaming = False
        self.callbackMap = {}
        self.tseq = 1
        
        self.sent = 0
        self.send_failed = 0
        self.received = 0
        self.delivered = 0
        self.missing = 0
        self.ooo = 0

        if debug:
            self.st = threading.Timer(1,self.stats)
            self.st.start()
        else:
            self.st = None

    def stats(self):
        print("sent: %i send-failed: %i received: %i delivered: %i missing: %i out-of-order: %i" % (self.sent, self.send_failed, self.received, self.delivered, self.missing, self.ooo))
        self.sent = 0
        self.send_failed = 0
        self.received = 0
        self.delivered = 0
        self.missing = 0
        self.ooo = 0
        self.st = threading.Timer(1,self.stats)
        self.st.start()

    def stop(self):
        if self.st:
            self.st.cancel()

    def get(self, key, blocking=False):
        reqdata = 'GET ' + key + '\r\n'
        self.transmit(reqdata)
        
        if blocking:
            self.sock.settimeout(None)

        data,addr = self.sock.recvfrom(65536)

        if blocking:
            self.sock.settimeout(self.timeout)

        return data.split('\r\n', 1)[1][:-2]

    def set(self, key, value):
        data = 'SET ' + key + ' ' + str(self.tseq) + ' ' + str(len(value)) + '\r\n' + str(value) + '\r\n'
        self.tseq += 1
        self.transmit(data)

    def stream(self, key, callback):
        if not callback:
            if key in self.callbackMap:
                del self.callbackMap[key]

                if len(v) == 0:
                    self.streaming = False

            return

        data = 'STREAM ' + key + '\r\n'
        self.transmit(data)

        seq = 0
        if key in self.callbackMap:
            seq = self.callbackMap[key][1]

        self.callbackMap[key] = (callback, seq)
        self.streaming = True

    def listen(self, blocking=False):
        if not self.streaming:
            raise AssertionError('no keys are enabled for streaming')
        
        doonce = True
        while doonce or blocking:
            doonce = False

            try:
                data,addr = self.sock.recvfrom(65536)
            except socket.timeout:
                continue
            
            if not data:
                print('warning: failed recvfrom()')
                continue

            self.received += 1

            try:
                key,seq,value = self.parseResponse(data)

                if seq <= self.callbackMap[key][1]:
                    self.ooo += 1
                    continue

                self.missing += seq-self.callbackMap[key][1]-1

                callback = self.callbackMap[key][0]
                self.callbackMap[key] = (callback, seq)

                callback(key, value)
                self.delivered += 1
            except MalformedResponseError:
                print('warning: bad response datagram on listen()')
                continue
            except KeyError:
                print('warning: got a response for an unbound key')
                continue

    def parseResponse(self, data):
        try:
            s = data.split('\r\n',1)
            command = s[0].split()
            key = command[0]
            seq = int(command[1])
            vallen = int(command[2])

            if len(s[1]) != vallen+2:
                raise MalformedResponseError

            value = s[1][0:vallen]
        except:
            raise MalformedResponseError
        return key, seq, value

    def transmit(self, data):
        try:
            self.sock.sendto(bytes(data, 'ascii'), self.hostaddr)
            self.sent += 1
        except socket.timeout:
            self.send_failed += 1
        except socket.error as e:
            # Consider network unreachable a failed send
            if e.errno != 101:
                raise e
            self.send_failed += 1
