import socket

class SocketWrapper(object):
    def __init__(self, address, port, socket_type, socket_timeout):
        self.address = address
        self.port = port
        self.socket_type = socket_type
        self.socket_timeout = socket_timeout
        self.socket = socket.socket(self.socket_type)
        self.socket.settimeout(self.socket_timeout)
        self.socket.bind((self.address,self.port))
    def receive_from(self, transformer_fn=lambda x: x, buffer_size=1, error_handler_fn=None):
        if error_handler_fn == None:
            error_handler_fn = lambda x: None
        value = None
        try:
            value, _ = self._socket_decision.recvfrom(buffer_size)
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
        


