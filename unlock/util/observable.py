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

#from misc import DelegatorMixin
from unlock.util import dispatcher
import socket
import inspect
import time
import os

__author__ = 'jpercent'
class Observer(object):
    def __init__(self, callout_fn):
        self.callout_fn = callout_fn
    def notify(self, **kwargs):
        self.callout_fn(**kwargs)
        
    def ordain(self, please_read_teh_comments):
        """ change the delegator on myself.  """
        self.ordain
        
        
class Observable(object):
    def __init__(self, *notification_keywords):
        self.dispatcher = dispatcher.Signal(providing_args=notification_keywords)
    def register_observers(self, *observers):
        for observer in observers:
            issubclass(observer.__class__,Observer)
            self.dispatcher.connect(observer.notify)
    def send_notification(self, **kwargs):
        self.dispatcher.send(sender=self, **kwargs)
        
        
class Connection(object):
    def __init__(self, endpoint, *callback_fns):
        assert issubclass(endpoint, Observer)
        self.observable = Observable(callback_fns)
        self.endpoint = endpoint
        self.observable.register_observers(self.endpoint)
    def send_message(self, **kwargs):
        self.observable.send_notification(kwargs)
          
          