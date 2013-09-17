from threading import Thread
import streamclient
import time

# API reference for irobot create sensorimotor system
#SERVER        = '172.24.98.206'
SERVER        = 'cns-ws26.bu.edu'
PORT          = 21567
 
ROBOT_SENSOR  = 'create/sensor.json'
ROBOT_AUDIO   = 'create/audio.raw'
ROBOT_VIDEO   = 'create/video.jpg'
ROBOT_BUMPERS = 'create/bumpers.json'

MOTOR_OUT     = 'motor/output.json'
ARM_OUT       = 'arm/output.json'
AUDIO_OUT     = 'audio/output.json'
VISION_OUT    = 'vision/output.json'

# Writer process prototype 
class AsimovWriter(Thread):
  def __init__(self, ns):
    Thread.__init__(self)
    self.running = True
    self.sc = streamclient.StreamClient(SERVER, PORT)
    self.ns = ns

  def process(self):
    pass

  def run(self):
    while self.running:
      self.process()

  def stop(self):
    self.running = False

  def set(self, key, value):
    self.sc.set(self.ns + '/' + key, value)

# Reader process prototype
class AsimovReader(Thread):
  def __init__(self, ns, key, timeout, debug=False):
    Thread.__init__(self)
    self.running = True
    self.sc = streamclient.StreamClient(SERVER, PORT, debug=debug)
    self.ns = ns
    self.key = key
    self.timeout = timeout
    self.lastSub = time.time()
    self.lastMsg = 0.0
    self.issilent = True
    self.sc.stream(self.ns + '/' + self.key, self.streamCallback)

  def streamCallback(self, key, value):
    self.lastMsg = time.time()
    self.issilent = False
    self.process(value)

  def process(self, value):
    pass

  def silent(self):
    pass

  def run(self):
    self.silent()

    while self.running:
      self.sc.listen()

      now = time.time()

      # re-transmit the stream subscription datagram once per second
      if now - self.lastSub > 1:
        self.sc.stream(self.ns + '/' + self.key, self.streamCallback)
        self.lastSub = now

      # if no data arrives for 'timeout' seconds, notify the process
      if not self.issilent and now - self.lastMsg > self.timeout:
        self.issilent = True
        self.silent()

  def stop(self):
    self.running = False
    self.sc.stop()

class AsimovDriver(Thread):
  def __init__(self, debug=False, **subthreads):
    """Provide control logic for a collection of Asimov readers and writers

    Initialize with named readers/writers
    e.g. AsimovDriver(reader1 = ..., writer1 = ...)

    Override process method using these names."""
    Thread.__init__(self)
    self.running = True
    self.debug = debug

    # Track subthreads for starting and stopping
    self.subthreads = subthreads.values()

    # Make subthreads object attributes, using the names we're given
    # e.g. AsimovDriver(wheels = AsimovWriter(...)) will have attribute
    # wheels
    for (k,v) in subthreads.items():
      self.__setattr__(k,v)

  def process(self):
    pass

  def silent(self):
    pass

  def run(self):
    while self.running:
      self.process()

  def start(self):
    """Start subthreads and self"""
    for thread in self.subthreads:
      thread.start()
    Thread.start(self)

  def stop(self):
    """Stop self and subthreads"""
    for thread in self.subthreads:
      if self.debug:
        print 'Trying to kill: ' + str(thread)
      thread.stop()
    for thread in self.subthreads:
      if thread.isAlive():
        thread.join()
    self.running = False
