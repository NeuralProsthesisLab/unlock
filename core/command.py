import socket
import cPickle
import json
from unlock.util import DatagramWrapper

class Command(object):
    def __init__(self, delta=None, decision=None, selection=None, data=None, json=False):
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.data = data
        self.json = json

    @staticmethod
    def serialize(command):
        if command.json:
            ret = json.dumps(command)
        else:
            ret = cPickle.dumps(command)
        return ret

    @staticmethod
    def deserialize(serialized_command, json=False):
        if json:
            ret = json.loads(serialized_command)
        else:
            ret = cPickle.loads(serialized_command)
        return ret
            
          
class CommandReceiverInterface(object):
    def next_command(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement the next_command method")
    
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement the stop method")
        
        
class CommandSenderInterface(object):
    def send(self, command):
        raise NotImplementedError("Every CommandSenderInterface must implement the send method")        
        
        
class DatagramCommandSender(object):
    def __init__(self):
        pass
        
        
class DatagramDecomposedCommandReceiver(CommandReceiverInterface):
    def __init__(self, address='127.0.0.1', decision_port=33445, selection_port=33446, data_port=33447, socket_timeout=0.001):
        self.decision_socket = DatagramWrapper(address, decision_port, socket_timeout)
        self.selection_socket = DatagramWrapper(address, selection_port, socket_timeout)
        self.data_socket = DatagramWrapper(address, data_port, socket_timeout)
        
    def next_command(self, delta_since_last_poll):
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
            
            
class InlineCommandReceiver(CommandReceiverInterface):
    def __init__(self):
        self.Q = []
        self.pos = 0
    
    def next_command(self):
        if self.pos == len(self.Q):
            ret = None
        else:
            ret = self.Q[self.pos]
            self.pos += 1
        return ret
    
    def stop(self):
        logger.debug("stop called")
    
    def put(self, command):
        self.Q.append(command)
    
