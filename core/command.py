import socket
import cPickle
import json
import logging
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
            
            
class PygletKeyboardCommand(Command):
    def __init__(self, symbol, modifiers):
        super(PygletKeyboardCommand, self).__init__()
        labels = [ord(c) for c in 'abcdefghijklmnopqrstuvwxyz_12345']
        if symbol == pyglet.window.key.UP:
            self.decision = 1
        elif symbol == pyglet.window.key.DOWN:
            self.decision = 2
        elif symbol == pyglet.window.key.LEFT:
            self.decision = 3 
        elif symbol == pyglet.window.key.RIGHT:
            self.decision = 4
        elif symbol == pyglet.window.key.SPACE:
            self.selection = 1
        elif symbol == pyglet.window.key.ESCAPE:
            self.stop = True
        elif symbol in labels:
            self.decision = labels.index(symbol) + 1        
            
            
class CommandReceiverInterface(object):
    def next_command(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement the next_command method")
        
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement the stop method")
        
        
class CommandSenderInterface(object):
    def send(self, command):
        raise NotImplementedError("Every CommandSenderInterface must implement the send method")        
        
        
class DatagramCommandReceiver(CommandReceiverInterface):
    def __init__(self, sink):
        self.sink = sink
        self.log = logging.getLogger(__name__)
        
    def next_command(self):        
        def error_handler(e):
            self.log.error("DatagramCommandReceiver failed ", exc_info=True)
            raise e
            
        command_size = int(self.sink.receive(4, error_handler))
        assert command_size > 0
            
        serialized_command = ''
        serialized_command = self.sink.receive(command_size, error_handler)
        command = Command.deserialize(serialized_command)
        return command
            
    def stop(self):
        self.sink.close()
            
    @staticmethod
    def create(address='', port=31337, socket_timeout=0.001):
        return DatagramCommandReceiver(DatagramWrapper.create_sink(address, port, socket_timeout))
            
            
class DatagramCommandSender(object):
    def __init__(self, source):
        self.source = source
        self.log = logging.getLogger(__name__)
            
    def send(self, command):
        def error_handler(e):
            self.log.error("DatagramCommandSender failed ", exc_info=True)
            raise e
            
        bytes_sent = 0
        serialized_command = Command.serialize(command)
        bytes_sent += self.source.send(str(len(serialized_command)), error_handler)
        bytes_sent += self.source.send(serialized_command, error_handler)
        return bytes_sent
            
    def stop(self):
        self.source.close()
            
    @staticmethod
    def create(address='', port=31337):
        return DatagramCommandSender(DatagramWrapper.create_source(address, port))
            
            
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
            
            