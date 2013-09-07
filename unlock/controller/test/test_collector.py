
from unlock import PygletWindow, Collector, Canvas
from unlock.neural import *

import unittest
import pyglet


class CollectorTests(unittest.TestCase):       
    def testMSequenceCollector(self):
        pass

def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    