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
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from unlock.util import DatagramWrapper
from .classify import UnlockClassifier
from multiprocessing import Process, Queue
import socket
import pickle
import json
import logging
import pyglet
import time
import numpy as np


class Command(object):
    def __init__(self, delta=None, decision=None, selection=None, data=None, json=False):
        super(Command, self).__init__()        
        self.delta = delta
        self.decision = decision
        self.selection = selection
        self.data = data
        self.json = json
        
    def is_valid(self):
        return True
        
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
        super(PygletKeyboardCommand, self).__init__()
        self.stop = False
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
            
            
class RawSignalCommand(Command):
    def __init__(self, delta, raw_data_vector, samples, channels, timer):
        super(RawSignalCommand, self).__init__(delta)
        self.raw_data_vector = raw_data_vector
        self.samples = samples
        self.channels = channels
        self.timer = timer
        self.sequence_trigger_vector = np.zeros((samples, 1))
        self.sequence_trigger_time_vector = np.zeros((samples, 1))
        self.cue_trigger_vector = np.zeros((samples, 1))
        self.cue_trigger_time_vector = np.zeros((samples, 1))        
        self.logger = logging.getLogger(__name__)
        
    def __reset_trigger_vectors__(self):
        self.sequence_trigger_vector[-1] = 0
        self.sequence_trigger_time_vector[-1] = 0        
        self.cue_trigger_vector[-1] = 0
        self.cue_trigger_time_vector[-1] = 0

    def is_valid(self):
        return self.raw_data_vector.size > 0
    
    def set_sequence_trigger(self, sequence_trigger_value):
        self.sequence_trigger_vector[-1] = sequence_trigger_value
        self.sequence_trigger_time_vector[-1] = self.timer.elapsedMicroSecs()
        
    def set_cue_trigger(self, cue_trigger_value):
        self.cue_trigger_vector[-1] = cue_trigger_value
        self.cue_trigger_time_vector[-1] = self.timer.elapsedMicroSecs()
        
    def make_matrix(self):
        self.data_matrix = self.raw_data_vector.reshape((self.samples, self.channels))
        self.matrix = np.hstack((self.data_matrix, self.sequence_trigger_vector, self.sequence_trigger_time_vector, self.cue_trigger_vector, self.cue_trigger_time_vector))
        self.__reset_trigger_vectors__()
        self.logger.debug("Data = ", self.matrix)
        
        
class CommandReceiver(object):
    def __init__(self):
        super(CommandReceiver, self).__init__()        
    
    def next_command(self, *args, **kwargs):
        raise NotImplementedError("Every CommandReceiver must implement the next_command method")
        
    def stop(self):
        raise NotImplementedError("Every CommandReceiver must implement the stop method")
        
            
class CommandSenderInterface(object):
    def send(self, command):
        raise NotImplementedError("Every CommandSenderInterface must implement the send method")        
        
        
class DatagramCommandReceiver(CommandReceiver):
    def __init__(self, source):
        super(DatagramCommandReceiver, self).__init__()                
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
        super(DatagramCommandSender, self).__init__()        
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
            
            
class InlineCommandReceiver(CommandReceiver):
    def __init__(self):
        super(InlineCommandReceiver, self).__init__()
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
            
            
class ClassifiedCommandReceiver(CommandReceiver):
    def __init__(self, command_receiver, classifier):
        super(ClassifiedCommandReceiver, self).__init__()
        self.command_receiver = command_receiver
        self.classifier = classifier
        
    def next_command(self, delta):
        command = self.command_receiver.next_command(delta)
        assert command != None
        classified_command = self.classifier.classify(command)
        assert classified_command != None
        return classified_command
        
    def stop(self):
        pass
            
          
class RawInlineSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer):
        super(RawInlineSignalReceiver, self).__init__()        
        self.signal = signal
        self.timer = timer
        
    def next_command(self, delta):
        samples = self.signal.acquire()
        
        if samples is not None and samples > 0:
            c_data = self.signal.getdata(samples)
            
            raw_data_vector = np.array(c_data)
            
            assert raw_data_vector.size % self.signal.channels() == 0
            if raw_data_vector[-1] == 0:
                raw_data_vector[-1] = self.timer.elapsedMicroSecs()
            raw_command = RawSignalCommand(delta, raw_data_vector, samples/self.signal.channels(), self.signal.channels(), self.timer)
        else:
            raw_command = RawSignalCommand(delta, np.array([]), 1, self.signal.channels(), self.timer)
            
        if raw_command.is_valid():
            raw_command.make_matrix()
            
        assert raw_command != None
        
        return raw_command
            
    def stop(self):
        pass
        
        
class DeltaCommandReceiver(CommandReceiver):
    def __init__(self):
        super(DeltaCommandReceiver, self).__init__()
            
    def next_command(self, delta):
        return Command(delta)
        
        
class CommandReceiverFactory(object):
    Delta=0
    Raw=1
    Classified=2
    Datagram=3
    Inline=4
    Multiprocess=5
    @staticmethod
    def map_factory_method(string):
        map_ = { 'delta': CommandReceiverFactory.Delta, 'raw' : CommandReceiverFactory.Raw,
                'classified': CommandReceiverFactory.Classified, 'datagram': CommandReceiverFactory.Datagram,
                'inline': CommandReceiverFactory.Inline, 'multiprocess': CommandReceiverFactory.Multiprocess}
        return map_[string]
                
                
    @staticmethod
    def create(factory_method=None, signal=None, timer=None, classifier=None, source=None):
        print ("RECATE command ", signal)
        if factory_method == CommandReceiverFactory.Delta or factory_method == None:
            return DeltaCommandReceiver()
        elif factory_method == CommandReceiverFactory.Raw:
            return RawInlineSignalReceiver(signal, timer)
        elif factory_method == CommandReceiverFactory.Classified:
            return ClassifiedCommandReceiver(RawInlineSignalReceiver(signal, timer), classifier)
        elif factory_method == CommandReceiverFactory.Datagram:
            return DatagramCommandReceiver(source)
        elif factory_method == CommandReceiverFactory.Inline:
            return InlineCommandReceiver()
        elif factory_method == CommandReceiverFactory.Multiprocess:
            return MultiProcessCommandReceiver(ClassifiedCommandReceiver(RawInlineSignalReceiver(signal, timer), classifier))
        else:
            raise LookupError('CommandReceiver does not support the factory method identified by '+str(factory_method))
        
def command_receiver_fn(Q, classifier, classifier_args, args):
    from unlock import unlock_runtime
    import unlock.context
    
    print('queue, classifier, classifer_args, args ', classifier, classifier_args, args)
    
    factory = unlock_runtime.UnlockFactory(args)
    app_ctx = unlock.context.ApplicationContext(factory)
    assert args['decoder'] == 'inline'
    factory.signal = app_ctx.get_object(args['signal'])
    factory.decoder = app_ctx.get_object(args['decoder'])
    command_receiver = factory.decoder.create_receiver(classifier_args, classifier)
    import time
    start = time.time()
    while True:
        command = command_receiver.next_command(time.time() - start)
        # can't pickle the C++ object
        command.timer = None
        Q.put(command)
        
        
class MultiProcessCommandReceiver(CommandReceiver):
    def __init__(self, classifier, classifier_args, args):
        super(MultiProcessCommandReceiver, self).__init__()        
        self.Q = Queue()
        self.args = args
        self.args['decoder'] = 'inline'
        self.process = Process(target=command_receiver_fn, args=(self.Q, classifier, classifier_args, self.args))
        self.process.start()
        
    def next_command(self, delta):
        return self.Q.get()
        
    def stop(self):
        self.process.terminate()
        self.process.join()
        
        
class InlineDecoder(object):
    def __init__(self, factory_method, signal, timer):
        super(InlineDecoder, self).__init__()
        self.factory_method = factory_method
        self.signal = signal
        self.timer = timer
        
    def shutdown(self):
        self.signal.stop()
        self.signal.close()
        
    def stop(self):
        raise Exception("WTF")
        
    def create_receiver(self, args, classifier_type=None):
        classifier_obj = UnlockClassifier.create(classifier_type, args)
        return CommandReceiverFactory.create(factory_method=self.factory_method, signal=self.signal,
                                             timer=self.timer, classifier=classifier_obj)
        
        
class MultiProcessDecoder(object):
    def __init__(self, args):
        super(MultiProcessDecoder, self).__init__()
        self.args = args
        self.mp_cmd_receiver = None
        
    def shutdown(self):
        if self.mp_cmd_receiver != None:
            self.mp_cmd_receiver.stop()
        
    def stop(self):
        pass    
        
    def create_receiver(self, args, classifier_type=None):
        self.mp_cmd_receiver = MultiProcessCommandReceiver(classifier_type, args, self.args)
        return self.mp_cmd_receiver
#        classifier_obj = UnlockClassifier.create(classifier_type, args)
 #       return CommandReceiverFactory.create(factory_method=self.factory_method, signal=self.signal, timer=self.timer, classifier=classifier_obj)
        
        