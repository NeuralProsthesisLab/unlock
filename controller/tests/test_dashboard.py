
from unlock import PygletWindow, Collector, Dashboard, Canvas

import unittest
import pyglet


class DashboardTests(unittest.TestCase):       
    def testDashboard(self):
        window = PygletWindow(fullscreen=True, show_fps=True)
        collector = Collector.create_msequence_collector(window, standalone=False)
        collector1 = Collector.create_msequence_collector(window, standalone=False)
        dashboard = Dashboard.create(window, [collector, collector1])
        dashboard.activate()
        window.start()        
        window.close()
        
        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    