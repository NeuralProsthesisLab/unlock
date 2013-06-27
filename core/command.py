from unlock.core.util import sockets
import socket

class BaseCommand(object):
    def __init__(self, delta, decision, selection):
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.data = data
        
class CommandReceiverInterface(object):
    def get_next_command(self):
        raise NotImplementedError("Every CommandReceiverInterface must get_next_command")
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must get_next_command")
        
class SocketBasedCommandReceiver(CommandReceiverInterface):
    def __init__(self, address='127.0.0.1', decision_port=33445, selection_port=33446, data_port=33447, socket_family=socket.AF_INET, socket_type=socket.SOCK_DGRAM, socket_timeout=0.001):
        self.decision_socket = SocketWrapper(address, decision_port, socket_family, socket_type, socket_timeout)
        self.selection_socket = SocketWrapper(address, selection_port, socket_family, socket_type, socket_timeout)
        self.data_socket = SocketWrapper(address, data_port, socket_family, socket_type, socket_timeout)
    def get_next_command(self, delta_since_last_poll):
        decision = self.decision_socket.receive(int)
        selection = self.selection_socket.receive(int)
        data = []
        done = False
        while not done:
            def stop(socket_error):
                done = True
            self.data_socket.receive(lambda x: data.append(json.loads(x)), 64, stop)            
        return BaseCommand(delta_since_last_poll, decision, selection, data)
    def stop(self):
        self.decision_socket.close()
        self.selection_socket.close()
        self.data_socket.close()
        
        