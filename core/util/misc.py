import dispatcher
import socket

class Observer(object):
    def __init__(self, callout_fn):
        self.callout_fn = callout_fn
    def notify(self, **kwargs):
        self.callout_fn(**kwargs)
        
        
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
        

class DatagramWrapper(object):
    def __init__(self, address, port, socket_timeout):
        self.address = address
        self.port = port
        self.socket_timeout = socket_timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.socket_timeout)
        self.socket.bind((self.address,self.port))
    def receive(self, transformer_fn=lambda x: x, buffer_size=1, error_handler_fn=None):
        if error_handler_fn == None:
            error_handler_fn = lambda x: None
        value = None
        try:
            value = self.socket.recv(buffer_size)
            value = transformer_fn(value)
        except socket.timeout, e:
            error_handler_fn(e)
        except socket.error, e:
            error_handler_fn(e)
        except ValueError, e:
            error_handler_fn(e)
        return value
    def stop(self):
        self.socket.close()
        

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
        
