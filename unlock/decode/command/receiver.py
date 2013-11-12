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
from unlock.decode.classify import UnlockClassifier
from unlock.decode.command import RawSignalCommand, Command
import socket
import pickle
import json
import numpy as np


class CommandReceiver(object):
    def __init__(self):
        super(CommandReceiver, self).__init__()        
    
    def next_command(self, *args, **kwargs):
        raise NotImplementedError("Every CommandReceiver must implement the next_command method")
        
    def stop(self):
        pass
            
            
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
        
        
class FileSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer):
        super(FileSignalReceiver, self).__init__()        
        self.signal = signal
        self.timer = timer
        self.calls = 0
        
    def next_command(self, delta):
        samples = self.signal.acquire()
        self.calls += 1
        if samples is not None and samples > 0:
            matrix = self.signal.getdata(samples)
            # XXX - the rawcmd.make_matrix stuff is a hack.  perhaps this should be a filerawcommand?
            raw_command = RawSignalCommand(delta, matrix, samples/self.signal.channels(), self.signal.channels(), self.timer)
            raw_command.matrix = matrix
            raw_command.data_matrix = matrix[:,:-RawSignal.TriggerCount]
        else:
            raise EOFError("FileSignalReceiver: FileSignal complete; calls = "+str(self.calls))
            
        assert raw_command != None
        return raw_command
            
            
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
            
            
class DeltaCommandReceiver(CommandReceiver):
    def __init__(self):
        super(DeltaCommandReceiver, self).__init__()
            
    def next_command(self, delta):
        return Command(delta)
        
        
class FileSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer):
        super(FileSignalReceiver, self).__init__()        
        self.signal = signal
        self.timer = timer
        self.calls = 0
        
    def next_command(self, delta):
        samples = self.signal.acquire()
        self.calls += 1
        if samples is not None and samples > 0:
            matrix = self.signal.getdata(samples)
            # XXX - the rawcmd.make_matrix stuff is a hack.  perhaps this should be a filerawcommand?
            raw_command = RawSignalCommand(delta, matrix, samples/self.signal.channels(), self.signal.channels(), self.timer)
            raw_command.matrix = matrix
            raw_command.data_matrix = matrix[:,:-RawSignal.TriggerCount]
        else:
            raise EOFError("FileSignalReceiver: FileSignal complete; calls = "+str(self.calls))
            
        assert raw_command != None
        return raw_command
            
            
class GeneratedSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer, command_receiver=None):
        self.signal = signal
        self.timer = timer
        if command_receiver == None:
            def create_raw_command(delta, data, samples, channels, timer):
                return RawSignalCommand(delta, data, samples, channels, timer)
            self.generate_next = create_raw_command
        else:
            self.generate_next = command_receiver.next_command
    def next_command(self, delta, samples=None):
        matrix = self.signal.generate_samples(samples)
        if samples is not None:
            assert samples == matrix.size
        raw_command = self.generate_next(delta, matrix, matrix.shape[0], self.signal.channels, self.timer)
        if raw_command.is_valid():
            raw_command.make_matrix()
            
        #print("data matrix = ", raw_command.data_matrix)
        return raw_command
            
            
class MultiProcessCommandReceiver(CommandReceiver):
    def __init__(self, classifier, classifier_args, args):
        super(MultiProcessCommandReceiver, self).__init__()        
        self.Q = Queue()
        self.args = args
        self.args['decoder'] = 'inline'
        self.process = Process(target=remote_receive_next_command, args=(self.Q, classifier, classifier_args, self.args))
        self.process.start()
        
    def next_command(self, delta):
        return self.Q.get()
        
    def stop(self):
        self.process.terminate()
        self.process.join()
        
#@staticmethod 
def remote_receive_next_command(Q, classifier, classifier_args, args):
    from unlock import unlock_runtime
    import unlock.context
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
        
            
class CommandReceiverFactory(object):
    Delta=0
    Raw=1
    Classified=2
    Datagram=3
    Inline=4
    Multiprocess=5
    
    @staticmethod
    def map_factory_method(string):
        map_ = {'delta': CommandReceiverFactory.Delta, 'raw': CommandReceiverFactory.Raw,
                'classified': CommandReceiverFactory.Classified, 'datagram': CommandReceiverFactory.Datagram,
                'inline': CommandReceiverFactory.Inline, 'multiprocess': CommandReceiverFactory.Multiprocess}
        return map_[string]
                
    @staticmethod
    def create(factory_method=None, signal=None, timer=None, classifier=None,
               source=None, chained_receiver=None):
        #print ("RECATE command ", signal)
        if factory_method == CommandReceiverFactory.Delta or factory_method is None:
            return DeltaCommandReceiver()
        elif factory_method == CommandReceiverFactory.Raw:
            return RawInlineSignalReceiver(signal, timer)
        elif factory_method == CommandReceiverFactory.Classified:
            if chained_receiver is None:
                from unlock.decode.acquire import MemoryResidentFileSignal
                # XXX - this is a quick hack, but this should be refactored.  Perhaps the base command
                #       receiver construction should happen in the main factory and be injected
                if type(signal) == MemoryResidentFileSignal:
                    print("creating memory resident file signal")
                    chained_receiver = FileSignalReceiver(signal, timer)
                else:
                    chained_receiver = RawInlineSignalReceiver(signal, timer)
            return ClassifiedCommandReceiver(chained_receiver, classifier)
        elif factory_method == CommandReceiverFactory.Datagram:
            return DatagramCommandReceiver(source)
        elif factory_method == CommandReceiverFactory.Inline:
            return InlineCommandReceiver()
        elif factory_method == CommandReceiverFactory.Multiprocess:
            return MultiProcessCommandReceiver(ClassifiedCommandReceiver(RawInlineSignalReceiver(signal, timer), classifier))
        else:
            raise LookupError('CommandReceiver does not support the factory method identified by '+str(factory_method))
            
            