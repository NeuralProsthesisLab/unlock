from .. import switch

import threading
import time
import random
import unittest


class AttrTest(object):
    def __init__(self):
        super(AttrTest, self).__init__()
        self.a = 0
        self.b = 1
        self.c = 2
        
    def d(self):
        self.d_value = True
        
    def e(self, e, e1):
        self.e_value = e
        self.e1_value = e1
        
        
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
    
    