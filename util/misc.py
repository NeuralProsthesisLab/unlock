import dispatcher
import socket
import inspect
import os


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
    def __init__(self, address, port, chunk_size=1048576):
        self.address = address
        self.port = port
        self.chunk_size = chunk_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
    def stop(self):
        self.socket.close()
            
    @staticmethod
    def create_sink(address, port, socket_timeout, chunk_size=1048576):
        return DatagramSink(address, port, socket_timeout, chunk_size)
            
    @staticmethod 
    def create_source(address, port, chunk_size=1048576):
        return DatagramSource(address, port, chunk_size)      
        
class DatagramSink(DatagramWrapper):
    def __init__(self, address, port, socket_timeout=0.001, chunk_size=1048576):
        super(DatagramSink, self).__init__(address, port, chunk_size)
        self.socket_timeout = socket_timeout
        self.socket.settimeout(self.socket_timeout)
        self.socket.bind((self.address,self.port))
            
    def receive(self, buffer_size=1, error_handler_fn=lambda x: None):
        value = None
        try:
            value = self.__recv__(buffer_size)
        except socket.timeout, e:
            error_handler_fn(e)
        except socket.error, e:
            error_handler_fn(e)
        except ValueError, e:
            error_handler_fn(e)
            
        return value
            
    def __recv__(self, buffer_size):
        obj = ''
        chunk_size = self.chunk_size
        consumed = 0
        
        while consumed < buffer_size:
            if buffer_size < chunk_size:
                chunk_size = buffer_size
            received = self.socket.recv(chunk_size)
            obj = obj.join(received)
            consumed += chunk_size
          
        return obj if obj != '' else None
          
            
class DatagramSource(DatagramWrapper):
    def send(self, buf, error_handler_fn=None):
        bytes_sent = 0
        try:
            bytes_sent = self.__snd__(buf)
        except socket.timeout, e:
            error_handler_fn(e)
        except socket.error, e:
            error_handler_fn(e)
        except ValueError, e:
            error_handler_fn(e)
            
        return bytes_sent
            
    def __snd__(self, buf):
        buffer_size = len(buf)
        chunk_size = self.chunk_size
        sent = 0
            
        while sent < buffer_size:
            if chunk_size < buffer_size:
                chunk_size = buffer_size
            send_buf = buf[sent:sent+chunk_size]
            sent += self.socket.sendto(send_buf, (self.address, self.port))            
                
        return sent
          
            
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
            
            
class RunState(object):
    def __init__(self):
        self.stop()
        
    def start(self):
        self.state = 'started'
        
    def pause(self):
        self.state = 'paused'
        
    def stop(self):
        self.state = 'stopped'
        
    def get_state(self):
        return self.state
        
    def is_started(self):
        return True if self.state == 'started' else False
        
    def is_paused(self):
        return True if self.state == 'paused' else False
        
    def is_stopped(self):
        return True if self.state == 'stopped' else False
        
        