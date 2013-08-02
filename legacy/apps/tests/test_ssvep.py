from .. import *
import unittest
import threading
import time

class SSVEPTests(unittest.TestCase):
    """Test suite for the ssvep module"""
    def testSSVEP(self):
            
        self.assertEquals(c.delta, c1.delta)
        self.assertEquals(c.decision, c1.decision)
        self.assertEquals(c.selection, c1.selection)        
        self.assertEquals(c.data, c1.data)
            
            
def getSuite():
    return unittest.makeSuite(SSVEPTests,'test')

if __name__ == "__main__":
    unittest.main()
