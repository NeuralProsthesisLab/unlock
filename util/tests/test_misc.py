from .. import switch

import threading
import time
import random
import unittest

class MiscTests(unittest.TestCase):
    def testSwitch(self):
        correct = False
        incorrect = False
        val = 'v'
        for case in switch(val):
            if case('v'):
                correct = True
                break
            if case('d'):
                incorrect = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        correct = False
        incorrect = False
        val = 'd'
        for case in switch(val):
            if case('v'):
                incorrect = True
                break
            if case('d'):
                correct = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        correct = False
        incorrect = False
        val = ['efg', 'v']
        for case in switch(val):
            if case('v'):
                incorrect = True
                break
            if case('d'):
                incorrect = True
                break
            if case (['efg', 'v']):
                correct = True
                break
            if case ():
                incorrect = True
                break
        self.assertTrue(correct and not incorrect)
        
        
def getSuite():
    return unittest.makeSuite(MiscTests,'test')

if __name__ == "__main__":
    unittest.main()
    
    