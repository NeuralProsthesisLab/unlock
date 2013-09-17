class UnlockAcquisition(object):
    """
    The basic data acquisition class.
    """
    def __init__(self, device, channels, frequency):
        self._device = device
        self.channels = channels
        self.frequency = frequency
        self._samples = 0

    def open(self, *args):
        """Open a data connection handle to the hardware device"""
        status = False
        if len(args) > 0:
            status = self._device.open(args)
        else:
            status = self._device.open()
        return status

    def init(self, *args):
        """Initialize hardware"""
        status = False
        if len(args) > 0:
            status = self._device.init(args)
        else:
            status = self._device.init()
        return status

    def start(self):
        """Start data acquisition and streaming"""
        return self._device.start()

    def stop(self):
        """Stop data acquisition and streaming"""
        return self._device.stop()

    def close(self):
        """Close handle to the hardware device"""
        return self._device.close()

    def acquire(self):
        """Synchronous data acquisition"""
        self._samples = self._device.acquire()
        return self._samples

    def getdata(self):
        """Retrieve the last set of buffered sample data"""
        return self.getdata(self.channels*self._samples)