
from unlock.controller import PygletWindow, Collector, Dashboard, Canvas

import unittest
import pyglet
from unlock.bci import FakeBCI

class DashboardTests(unittest.TestCase):       
    def testDashboard(self):
        window = PygletWindow(fullscreen=False, show_fps=True)
        bci = FakeBCI()
        collector = Collector.create_multi_centered_msequence_collector(window, bci, standalone=False)
        collector1 = Collector.create_single_centered_msequence_collector(window, bci, standalone=False)

        dashboard = Dashboard.create(window, [collector, collector1], bci)
        dashboard.activate()
        window.start()        
        window.close()                        

        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    