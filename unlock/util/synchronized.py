import logging
import traceback
from threading import RLock, currentThread

# Original code by Anand Balachandran Pillai (abpillai at gmail.com)
# http://code.activestate.com/recipes/533135/
class synchronized(object):
    """ Class enapsulating a lock and a function allowing it to be used as
    a synchronizing decorator making the wrapped function thread-safe """

    def __init__(self, *args):
        self.lock = RLock()
        self.logger = logging.getLogger(__name__)

    def __call__(self, f):
        def lockedfunc(*args, **kwargs):
            try:
                self.lock.acquire()
                self.logger.debug("Acquired lock [%s] thread [%s]" % (self.lock, currentThread()))
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    raise
            finally:
                self.lock.release()
                self.logger.debug("Released lock [%s] thread [%s]" % (self.lock, currentThread()))
        return lockedfunc
