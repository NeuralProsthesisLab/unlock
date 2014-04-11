# Copyright (c) James Percent and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.import socket

__author__ = 'jpercent'

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

