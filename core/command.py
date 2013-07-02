from unlock.core.util import misc
import socket

class BaseCommand(object):
    def __init__(self, delta, decision, selection):
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.data = data
        
class CommandReceiverInterface(object):
    def get_next_command(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement get_next_command")
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement stop")
        
class DatagramBasedCommandReceiver(CommandReceiverInterface):
    def __init__(self, address='127.0.0.1', decision_port=33445, selection_port=33446, data_port=33447, socket_timeout=0.001):
        self.decision_socket = DatagramWrapper(address, decision_port, socket_timeout)
        self.selection_socket = DatagramWrapper(address, selection_port, socket_timeout)
        self.data_socket = DatagramWrapper(address, data_port, socket_timeout)
    def get_next_command(self, delta_since_last_poll):
        decision = self.decision_socket.receive_from(int)
        selection = self.selection_socket.receive_from(int)
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
        
        
