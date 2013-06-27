from .. import SocketWrapper
from .. import Observer, Observable
from .. import switch

import socket
import threading
import time
import random
import unittest

class Model(object):
    def __init__(self, val):
        self.val = val

class MiscTests(unittest.TestCase):
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

    def testSocketWrapper(self):
        socket_wrapper = SocketWrapper('', 31337, socket.AF_INET, socket.SOCK_DGRAM, 0.001)
        val = socket_wrapper.receive_from()
        self.assertEquals(None, val)
            
        def async_sendto():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print 'sending too...'
            s.sendto('42', ('', 31337))                
        t = threading.Thread(target = async_sendto, args = ())
        t.start()
        
        count = 0
        def error_fn(error):
            print error
            
        while val == None:
            val = socket_wrapper.receive_from(int, 2, error_handler_fn = error_fn)
            time.sleep(.5)
            count += 1
            if count > 2:
                self.assertFalse(True)
                
        t.join()
        self.assertEquals(42, val)
        
    def testSwitch(self):
        correct = False
        incorrect = False
        val = 'v'
        for case in switch(val):
            if case('v'):
                correct = True
                break
            if case('d'):
                incorrect = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        correct = False
        incorrect = False
        val = 'd'
        for case in switch(val):
            if case('v'):
                incorrect = True
                break
            if case('d'):
                correct = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        correct = False
        incorrect = False
        val = ['efg', 'v']
        for case in switch(val):
            if case('v'):
                incorrect = True
                break
            if case('d'):
                incorrect = True
                break
            if case (['efg', 'v']):
                correct = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        
def getSuite():
    return unittest.makeSuite(MiscTests,'test')

if __name__ == "__main__":
    unittest.main()
    
    