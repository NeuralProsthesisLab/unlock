from .. import switch, DelegatorMixin

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
        
    def testDelegator(self):
        d = DelegatorMixin()
        a = AttrTest()
        a1 = AttrTest()
        a1.a = 111
        a1.b = 111
        a1.c = 111
        
        a1.c = "A1F"
        d.add_delegate(a)
        d.add_delegate(a1)
        d.g = "DG"
        d.c = 222
        d.d()
        d.e(1,3)
        
        self.assertEquals(0, d.a)
        self.assertEquals(1, d.b)
        self.assertEquals(222, d.c)
        self.assertEquals(True, d.d_value)
        self.assertEquals(1, d.e_value)
        self.assertEquals(3, d.e1_value)
        self.assertEquals("DG", d.g)
        
        
def getSuite():
    return unittest.makeSuite(MiscTests,'test')


if __name__ == "__main__":
    unittest.main()
    
    