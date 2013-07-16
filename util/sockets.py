import socket
    

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