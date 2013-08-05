#from misc import DelegatorMixin
import dispatcher
import socket
import inspect
import time
import os


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
          
          