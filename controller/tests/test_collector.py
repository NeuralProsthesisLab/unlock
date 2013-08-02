
from unlock import PygletWindow, Collector, Canvas

import unittest
import pyglet


class CollectorTests(unittest.TestCase):       
    def testMSequenceCollector(self):
        window = PygletWindow(fullscreen=True, show_fps=True)
        collector = Collector.create_multi_centered_msequence_collector(window)
        collector.activate()
        window.start()        
        window.close()


#    def test2(self):
#        window = PygletWindow(fullscreen=True, show_fps=True)
 #       collector = Collector.create_single_centered_msequence_collector(window)
 #       collector.activate()
 #       window.start()        
 #       window.close()        
        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    