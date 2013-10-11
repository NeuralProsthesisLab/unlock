# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import inspect
import os


class DelegatorMixin(object):
    def __init__(self):
        super(DelegatorMixin, self).__init__()
        self.delegates = set([])
        self.ordering = []
        
    def __getattr__(self, name):
        for delegate in self.ordering:
            try:
                return getattr(delegate, name)
            except:
                pass
        raise AttributeError(name)
            
    def add_delegate(self, delegate):
        if not delegate in self.delegates:
            self.delegates.add(delegate)
            self.ordering.append(delegate)
            
          
class Trigger(object):
    Null=0
    Start=1
    Stop=2
    Pause=3
    Cue=4
    Indicate=5
    Rest=6
    Up=7
    Right=8
    Down=9
    Left=10
    Repeat=11
    Complete=12
    Forward=13
    Back=14
    Select=15
    UsageDefined=16
    UsageDefined1=17
    UsageDefined2=18
        
        
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
            
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
           
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
              
              
class Resource(object):
    def __init__(self, path=None):
        if path == None:
            #os.path.dirname(inspect.getabsfile(unlock.Resource))
            self.path = os.path.dirname(inspect.getfile(Resource))+'/resource/'
        else:                
            self.path = path
        self.resources = []
        
    def reset_path(self, path):
        self.path = path
        
    def add_resource(self, resource):
        self.resources.append(resource)
            
            