
from unlock.util import DatagramWrapper

import socket
import pickle
import json
import logging
import pyglet
import time
import numpy as np


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
            ret = pickle.dumps(command)
        return ret
           
    @staticmethod
    def deserialize(serialized_command, json=False):
        if json:
            ret = json.loads(serialized_command)
        else:
            ret = pickle.loads(serialized_command)
        return ret
            
            
class PygletKeyboardCommand(Command):
    def __init__(self, symbol, modifiers):
        self.stop = False
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
            
            
class RawBCICommand(Command):
    def __init__(self, delta, raw_data_vector, samples, channels):
        super(RawBCICommand, self).__init__(delta)
        self.raw_data_vector = raw_data_vector
        self.samples = samples
        self.channels = channels
        self.sequence_trigger_vector = np.zeros((samples, 1))        
        self.cue_trigger_vector = np.zeros((samples, 1))
        self.logger = logging.getLogger(__name__)
        
    def __reset_trigger_vectors__(self):
        self.sequence_trigger_vector[-1] = 0
        self.cue_trigger_vector[-1] = 0
        
    def set_sequence_trigger(self, sequence_trigger_value):
        self.sequence_trigger_vector[-1] = sequence_trigger_value
        
    def set_cue_trigger(self, cue_trigger_value):
       self.cue_trigger_vector[-1] = cue_trigger_value
        
    def make_matrix(self):
        data_matrix = self.raw_data_vector.reshape((self.samples, self.channels))
        self.matrix = np.hstack((data_matrix, self.sequence_trigger_vector, self.cue_trigger_vector))
        self.__reset_trigger_vectors__()
        self.logger.debug("Data = ", self.matrix)
        
        
class CommandReceiverInterface(object):
    def next_command(self, *args, **kwargs):
        raise NotImplementedError("Every CommandReceiverInterface must implement the next_command method")
        
    def stop(self):
        raise NotImplementedError("Every CommandReceiverInterface must implement the stop method")
        
        
class CommandSenderInterface(object):
    def send(self, command):
        raise NotImplementedError("Every CommandSenderInterface must implement the send method")        
        
        
class DatagramCommandReceiver(CommandReceiverInterface):
    def __init__(self, source):
        self.source = source
        self.log = logging.getLogger(__name__)
        
    def next_command(self, delta):        
        def error_handler(e):
            self.log.error("DatagramCommandReceiver failed ", exc_info=True)
            raise e
            
        command_size = int(self.source.receive(4, error_handler))
        assert command_size > 0
            
        serialized_command = ''
        serialized_command = self.source.receive(command_size, error_handler)
        command = Command.deserialize(serialized_command)
        command.delta = delta
        return command
            
    def stop(self):
        self.source.close()
            
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
            
    def next_command(self, delta):
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
            
          
class RawInlineBCIReceiver(CommandReceiverInterface):
    def __init__(self, bci):
        self.bci = bci
        
    def next_command(self, delta):
        samples = None
        while samples == None or samples < 1:
            samples = self.bci.acquire()

#        print('samples = ', str(samples))
        done = False
        while not done:
            try:
                c_data = self.bci.getdata(samples)
                raw_data_vector = np.array(c_data)
                done = True
            except MemoryError:
                time.sleep(.1)
                continue
                #raw_data_vector = c_data[len(c_data)/2:]

        return RawBCICommand(delta, raw_data_vector, samples/self.bci.channels(), self.bci.channels())
        
    def stop(self):
        self.bci.stop()
        self.bci.close()


class DeltaCommandReceiver(CommandReceiverInterface):
    def next_command(self, delta):
        return Command(delta)