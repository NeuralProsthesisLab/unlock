
from unlock import PygletWindow, Collector

import unittest
import pyglet


class CollectorTests(unittest.TestCase):       
    def testMSequenceCollector(self):
        window = PygletWindow(fullscreen=False, show_fps=True)
        canvas = Canvas.create(window.width, window.height)
        collector = Collector.create_msequence_collector(window, canvas)
        collector.activate()
        window.start()        
        window.close()
        
        
def getSuite():
    return unittest.makeSuite(CollectorTests,'test')

if __name__ == "__main__":
    unittest.main()
    