from .. import DatagramWrapper

import socket
import threading
import time
import random
import unittest


class SocketsTests(unittest.TestCase):

    def testDatagramSink(self):
        socket_wrapper = DatagramWrapper.create_sink('', 31337, 0.001)
        val = socket_wrapper.receive()
        self.assertEquals(None, val)
            
        def async_sendto():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('sending too...')
            s.sendto('42', ('', 31337))                
        t = threading.Thread(target = async_sendto, args = ())
        t.start()
        
        count = 0
        def error_fn(error):
            print(error)
            
        while val == None:
            val = socket_wrapper.receive(2, error_handler_fn = error_fn)
            time.sleep(.5)
            count += 1
            if count > 2:
                self.assertFalse(True)
                
        t.join()
        self.assertEquals(42, int(val))
        count = 0
        while val == None:
            val = socket_wrapper.receive(2, error_handler_fn = error_fn)
            time.sleep(.5)
            count += 1
            if count > 2:
                break
                
    def testDatagramSourceSink(self):
        socket_wrapper = DatagramWrapper.create_sink('', 31337, 0.001)
        val = socket_wrapper.receive()
        self.assertEquals(None, val)
            
        def async_sendto():
            def send_error_fn(ex):
                print('send error ', ex)
                
            s = DatagramWrapper.create_source('', 31337)
            print('sending too...')
            s.send('42', send_error_fn)
        t = threading.Thread(target = async_sendto, args = ())
        t.start()
        
        count = 0
        def error_fn(error):
            print(error)
            
        while val == None:
            val = socket_wrapper.receive(2, error_handler_fn = error_fn)
            time.sleep(.5)
            count += 1
            if count > 2:
                self.assertFalse(True)
                
        t.join()
        self.assertEquals(42, int(val))
         
         
def getSuite():
    return unittest.makeSuite(SocketsTests,'test')

if __name__ == "__main__":
    unittest.main()
    
    