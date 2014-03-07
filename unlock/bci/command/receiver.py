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
from unlock.state import RunState
from unlock.bci.decode import UnlockDecoder

from unlock.bci.command.command import RawSignalCommand, Command
import socket
import pickle
import json
import logging
import numpy as np


class CommandReceiver(object):
    def __init__(self, state=None):
        super(CommandReceiver, self).__init__()
        if not state:
            state = RunState()
            state.run()
            
        self.state = state
        
    def is_running(self):
        return self.state.is_running()
        
    def start(self):
        self.state.run()
        
    def stop(self):
        self.state.stop()
    
    def next_command(self, *args, **kwargs):
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
        self.queue = []
        self.position = 0
            
    def next_command(self, delta):
        if self.position == len(self.queue):
            ret = None
        else:
            ret = self.queue[self.position]
            self.position += 1
        return ret
            
    def put(self, command):
        self.queue.append(command)
            
            
class DecodingCommandReceiver(CommandReceiver):
    def __init__(self, command_receiver, decoder, state=None):
        super(DecodingCommandReceiver, self).__init__(state=state)
        self.logger = logging.getLogger(__name__)        
        self.command_receiver = command_receiver
        self.decoder = decoder
    
    def start(self):
        super(DecodingCommandReceiver, self).start()
        self.command_receiver.start()
        self.decoder.start()
        
    def stop(self):
        self.decoder.stop()
        self.command_receiver.stop()        
        super(DecodingCommandReceiver, self).stop()
        
    def next_command(self, delta):
        command = self.command_receiver.next_command(delta)
        if not self.is_running():
            self.logger.warning('DecodingCommandReceiver: poll while not running; returning empty command')
            return Command(delta)
            
        assert command
        if command.is_valid():
            command = self.decoder.decode(command)
        assert command
        return command
        
        
class FileSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer):
        super(FileSignalReceiver, self).__init__()        
        self.signal = signal
        self.timer = timer
        self.calls = 0
        
    def next_command(self, delta):
        samples = self.signal.acquire()
        self.calls += 1
        if samples and samples > 0:
            matrix = self.signal.getdata(samples)
            raw_command = RawSignalCommand(delta, matrix, samples/self.signal.channels(), self.signal.channels(), self.timer)
            raw_command.matrix = matrix
            raw_command.data_matrix = matrix[:, :-RawSignalCommand.TriggerCount]
        else:
            raise EOFError("FileSignalReceiver: FileSignal complete; calls = "+str(self.calls))
            
        assert raw_command
        return raw_command
        
        
class RawInlineSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer):
        super(RawInlineSignalReceiver, self).__init__()        
        self.signal = signal
        self.timer = timer
        
    def next_command(self, delta):
        samples = self.signal.acquire()
        if samples and samples > 0:
            c_data = self.signal.getdata(samples)
            
            raw_data_vector = np.array(c_data)
            assert raw_data_vector.size % self.signal.channels() == 0
            assert raw_data_vector[-1] == 0
            raw_data_vector[-1] = self.timer.elapsedMicroSecs()
            raw_command = RawSignalCommand(delta, raw_data_vector, samples/self.signal.channels(),
                self.signal.channels(), self.timer)
        else:
            raw_command = RawSignalCommand(delta, np.array([]), 1, self.signal.channels(), self.timer)
            
        if raw_command.is_valid():
            raw_command.make_matrix()
            
        assert raw_command
        return raw_command
        
        
class DeltaCommandReceiver(CommandReceiver):
    def __init__(self):
        super(DeltaCommandReceiver, self).__init__()
            
    def next_command(self, delta):
        return Command(delta)


class GeneratedSignalReceiver(CommandReceiver):
    def __init__(self, signal, timer, command_receiver=None):
        self.signal = signal
        self.timer = timer
        if not command_receiver:
            def create_raw_command(delta, data, samples, channels, timer):
                return RawSignalCommand(delta, data, samples, channels, timer)
            self.generate_next = create_raw_command
        else:
            self.generate_next = command_receiver.next_command

    def next_command(self, delta, samples=None):
        matrix = self.signal.generate_samples(samples)
        if samples:
            assert samples == matrix.size
        raw_command = self.generate_next(delta, matrix, matrix.shape[0], self.signal.channels, self.timer)
        if raw_command.is_valid():
            raw_command.make_matrix()

        return raw_command

