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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.import socket
    
__author__ = 'jpercent'

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
        except socket.timeout as e:
            error_handler_fn(e)
        except socket.error as e:
            error_handler_fn(e)
        except ValueError as e:
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
        except socket.timeout as e:
            error_handler_fn(e)
        except socket.error as e:
            error_handler_fn(e)
        except ValueError as e:
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
            
            