from .. import Observer, Observable

import socket
import threading
import time
import random
import unittest

class Model(object):
    def __init__(self, val):
        self.val = val


class ObserableTests(unittest.TestCase):
    def notify(self, **kwargs):
        self.last_args.append(kwargs)
        
    def testObserver(self):
        self.last_args = []
        observable = Observable('model')
        observer = Observer(self.notify)
        observable.register_observers(observer)
        m = Model(0)
        observable.send_notification(model=m)
        self.assertEqual(1, len(self.last_args))
        self.assertEqual(observable, self.last_args[0]['sender'])
        self.assertEqual(m, self.last_args[0]['model'])
        print self.last_args 
        observable.register_observers(observer, observer, observer)
        observable.send_notification()
        self.assertEqual(2, len(self.last_args))
        self.assertEqual(observable, self.last_args[0]['sender'])
        self.assertEqual(m, self.last_args[0]['model'])
        self.assertEqual(observable, self.last_args[0]['sender'])
        self.assertFalse(self.last_args[1].has_key('model'))
    
        
        new_observer1 = Observer(self.notify)
        new_observer2 = Observer(self.notify)
        m1 = Model(2)
        observable.register_observers(new_observer1, new_observer2)
        observable.send_notification(model = m1)
        self.assertEqual(5, len(self.last_args))
        rand = random.Random()
        self.assertEqual(observable, self.last_args[0]['sender'])
        self.assertEqual(m, self.last_args[0]['model'])
        self.assertEqual(observable, self.last_args[0]['sender'])
        self.assertFalse(self.last_args[1].has_key('model'))
        self.assertEqual(m1, self.last_args[rand.randint(2,4)]['model'])

def getSuite():
    return unittest.makeSuite(ObserableTests,'test')

if __name__ == "__main__":
    unittest.main()
    
    