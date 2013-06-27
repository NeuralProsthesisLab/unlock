import socket
import unlock_core

class SocketWrapper(object):
    def __init__(self, address, port, socket_type, socket_timeout, error_handler_fn=lambda x: None):
        self.address = address
        self.port = port
        self.socket_type = socket_type
        self.socket_timeout = socket_timeout
        self.socket = socket.socket(self.socket_type)
        self.socket.settimeout(self.socket_timeout)
        self.socket.bind((self.address,self.port))
        self.error_handler_fn = error_handler_fn
    def receive_from(self, transformer_fn=lambda x: x, buffer_size=1, error_handler_fn=self.error_handler_fn):
        value = None
        try:
            value, _ = self._socket_decision.recvfrom(buffer_size)
            value = transformer_fn(value)
        except socket.timeout, e:
            self.error_handler_fn(e)
        except socket.error, e:
            self.error_handler_fn(e)
        except ValueError, e:
            self.error_handler_fn(e)            
#        if 'decision' in self.debug_commands:
#            decision = self.debug_commands['decision']
#            del self.debug_commands['decision']        
        return value
    def stop(self):
        self.socket.close()
        
class SocketBasedCommandReceiver(unlock_core.CommandReceiverInterface):
    def __init__(self, address='127.0.0.1', decision_port=33445, selection_port=33446, data_port=33447, socket_type=socket.SOCK_DGRAM, socket_timeout=0.001):
        self.decision_socket = SocketWrapper(address, decision_port, socket_type, socket_timeout)
        self.selection_socket = SocketWrapper(address, decision_port, socket_type, socket_timeout)
        self.data_socket = SocketWrapper(address, decision_port, socket_type, socket_timeout)
    def get_next_command(self):
        decision = self.decision_socket.receive(int)
        selection = self.selection_socket.receive(int)
        data = []
        done = False
        while not done:
            def stop(socket_error):
                done = True
            self.data_socket.receive(lambda x: data.append(json.loads(x)), 64, stop)            
        return decision, selection, data
    def stop(self):
        self.decision_socket.close()
        self.selection_socket.close()
        self.data_socket.close()

