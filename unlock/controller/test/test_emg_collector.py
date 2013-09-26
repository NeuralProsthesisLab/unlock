
from unlock import PygletWindow, Collector, Canvas
from unlock.decode import RandomSignal

import unittest
import pyglet


class CollectorTests(unittest.TestCase):       
    def testEMGSequenceCollector(self):
        pass
        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    