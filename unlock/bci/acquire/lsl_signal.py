import uuid

import numpy as np

import unlock.bci.acquire.pylsl as lsl


class LSLSignal(object):
    """
    Consumes data from a named LSL outlet.
    """
    def __init__(self, stream_name, stream_type):
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.n_channels = 0

        self.outlet = None

        self.data = None
        self.inlets = dict()
        self.events = list()

    def open(self):
        uid = 'unlock-%s' % uuid.uuid1()
        info = lsl.StreamInfo(b'Presentation', b'Markers', 1, 0, 'int32',
                              uid.encode('ascii'))
        self.outlet = lsl.StreamOutlet(info)

        pred = "name='%s' and type='%s' or name='Presentation' or type='Gaze'" % (self.stream_name, self.stream_type)
        streams = lsl.resolve_bypred(pred.encode('ascii'))
        if len(streams) == 0:
            return False
        try:
            for stream in streams:
                self.inlets[stream.type()] = lsl.StreamInlet(stream)
                print(stream.type())
            self.n_channels = self.inlets[b'EEG'].channel_count + 2 + 1 + 1  # gaze channels, marker channel, timestamps
        except:
            return False
        return True

    def init(self):
        return True

    def start(self):
        try:
            for stream in self.inlets.values():
                stream.open_stream()
        except:
            return False
        return True

    def acquire(self):
        marker, timestamp = self.inlets[b'Markers'].pull_sample(timeout=0.0)
        if marker is not None:
            self.events.append((0, marker[0], timestamp))
        if b'Gaze' in self.inlets:
            gaze, timestamp = self.inlets[b'Gaze'].pull_sample(timeout=0.0)
            if gaze is not None:
                self.events.append((1, gaze, timestamp))
        eeg, timestamps = self.inlets[b'EEG'].pull_chunk()
        if len(eeg) == 0:
            return 0
        chunk = np.array(eeg)
        timestamps = np.array(timestamps, ndmin=2).T
        markers = np.zeros((len(chunk), 1))
        gaze = np.zeros((len(chunk), 2))
        clear = list()
        for event in self.events:
            idx = np.where(event[2] < timestamps)[0]
            if len(idx) == 0:
                break
            if event[0] == 0:
                markers[idx[0]] = event[1]
            else:
                gaze[idx[0]] = event[1]
            clear.append(event)
        for event in clear:
            self.events.remove(event)

        data = np.hstack((chunk, gaze, markers, timestamps))

        self.data = data.flatten()
        return len(self.data)

    def getdata(self, samples):
        return self.data[0:samples]

    def stop(self):
        for stream in self.inlets.values():
            stream.close_stream()
        return True

    def close(self):
        return True

    def channels(self):
        return self.n_channels
