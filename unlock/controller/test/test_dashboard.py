
from unlock.controller import PygletWindow, Collector, Dashboard, Canvas

import unittest
import pyglet
from unlock.decode import RandomSignal

class DashboardTests(unittest.TestCase):       
    def testDashboard(self):
        pass
        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    