
from unlock import PygletWindow, Collector, Canvas
from unlock.bci import FakeBCI

import unittest
import pyglet


class CollectorTests(unittest.TestCase):       
    def testEMGSequenceCollector(self):
        
        try:
           # from pynobio import Enobio
            #pynobio = True
            pynobio = False
            fakebci = False
        except Exception:
            pynobio = False
            fakebci = True
            
        
        if pynobio:
            try:
                bci = Enobio()
                bci.channels = 8
                if not bci.open():
                    print "enobio did not open"
                    raise Exception('enobio did not open')
                if not bci.start():
                    print 'enobio device did not start streaming'                                 
                    raise Exception('enobio device did not start streaming')                       
            except Exception, e:
                raise e
                fakebci = True

        ##if fakebci:
        #from unlock.bci import FakeBCI
        bci = FakeBCI()
            
            
        window = PygletWindow(fullscreen=True, show_fps=True)
        collector = Collector.create_emg_collector(window, bci, radius=.75)
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
    