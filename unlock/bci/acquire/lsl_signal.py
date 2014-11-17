import numpy as np

from unlock.bci.acquire.pylsl import StreamInlet, resolve_bypred


class LSLSignal(object):
    """
    Consumes data from a named LSL outlet.
    """
    def __init__(self, stream_name, stream_type):
        self.stream_name = stream_name
        self.stream_type = stream_type

        self.data = None
        self.inlet = None

    def open(self):
        pred = "name='%s' and type='%s'" % (self.stream_name, self.stream_type)
        streams = resolve_bypred(pred.encode('ascii'))
        if len(streams) == 0:
            return False

        try:
            self.inlet = StreamInlet(streams[0])
        except:
            return False
        return True

    def init(self):
        return True

    def start(self):
        try:
            self.inlet.open_stream()
        except:
            return False
        return True

    def acquire(self):
        chunk, timestamps = self.inlet.pull_chunk()
        if len(chunk) == 0:
            return 0
        chunk = np.array(chunk)
        timestamps = np.array(timestamps, ndmin=2).T
        data = np.hstack((chunk, timestamps))
        self.data = data.flatten()
        return len(self.data)

    def getdata(self, samples):
        return self.data[0:samples]

    def stop(self):
        self.inlet.close_stream()
        return True

    def close(self):
        return True

    def channels(self):
        return self.inlet.channel_count + 1
