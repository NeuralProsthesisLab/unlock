# Copyright (c) James Percent, Byron Galibrith  and Unlock contributors.
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
from unlock.bci.decode.decode import UnlockDecoder
from unlock.state import TrialState
import numpy as np
import time

SetResultHandler = 0
LogResultHandler = 1
PrintResultHandler = 2

#class HarmonicSumDecisionDecorator(UnlockDecoder):
#    def __init__(self, buffered_decoder, trial_controlled_decoder, feature_extractor, )

class HarmonicFeatureExtractor(UnlockDecoder):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, fs=256, n_electrodes=8, targets=(12.0, 13.0, 14.0, 15.0), target_window=0.1,
        nfft=2048, n_harmonics=1, selected_channels=None):
        
        super(HarmonicFeatureExtractor, self).__init__()
        
        self.fs = fs
        self.n_electrodes = n_electrodes
        self.targets = targets
        self.target_window = target_window
        self.nfft = nfft
        self.n_harmonics = n_harmonics
        
        self.selected_channels = selected_channels
        if selected_channels is None:
            self.selected_channels = range(self.n_electrodes)
             
        self.harmonics = list()
        
        freq_step = self.fs / self.nfft
        freqs = freq_step * np.arange(self.nfft/2 + 1)
        
        for i, target in enumerate(self.targets):
            harmonic_idx = list()
            for harmonic in range(1, self.n_harmonics+1):
                idx = np.where(np.logical_and(
                    freqs > harmonic * target - self.target_window,
                    freqs < harmonic * target + self.target_window))[0]
                harmonic_idx.append(idx)
            self.harmonics.append(harmonic_idx)
            
        self.file_handle = None
        self.output_file_prefix = 'Decoder'
        
    def start(self):
        assert self.file_handle == None
        self.file_handle = open("%s_%d.txt" % (self.output_file_prefix, time.time()), 'wb')
        
    def stop(self):
        assert self.file_handle != None
        self.file_handle.flush()
        self.file_handle.close()
        self.file_handle = None
        
    def decode(self, command):
        """
        The features used by harmonic sum decision are the summed magnitudes of one or more
        harmonics of the target frequencies across one or more channels of recorded data.
        """
        y = command.matrix[:, self.selected_channels]
        y -= np.mean(y, axis=0)
        y = np.abs(np.fft.rfft(y, n=self.nfft, axis=0))
        # XXX - frequency values are y (amplitude of each frequency)  nfft == 2048 (window size)
        #       
        #      calculate from nfft 
        command.scores = np.zeros(len(self.targets))
        for i in range(len(self.targets)):
            score = 0
            for harmonic in self.harmonics[i]:
                score += np.mean(y[harmonic, :])
            command.scores[i] = score
#        command.scores = self.extract_features(command.matrix)
        return command
        
        
class ScoredHarmonicSumDecision(UnlockDecoder):
    def __init__(self, threshold_decoder, targets):
        super(ScoredHarmonicSumDecision, self).__init__()
        self.threshold_decoder = threshold_decoder
        self.targets = targets
        
    def decode(self, command):
        """
        Find the largest frequency magnitude and determine if it meets
        threshold criteria.
        """
        assert hasattr(command, 'scores')
            
        command.winner = np.argmax(command.scores)
        command = self.threshold_decoder.decode(command)
            
        if command.accept:
            command.class_label = command.winner + 1
            np.set_printoptions(precision=2)
            result_string = "ScoredHarmonicSumDecision: %d (%.1f Hz)" % (command.class_label,
                self.targets[command.class_label])
                
            if command.confidence is not None:
                result_string = "%s [%.2f]" % (result_string, command.confidence)
                
        else:
            command.class_label = -1
            result_string = "ScoredHarmonicSumDecision: could not make a decision"
                
        print(result_string)
        return command
#       
#
## Somethings wind up being ugly for no good reason.
#class ResultHandler(object):
#    def __init__(self, result_handlers=()):
#        super(ResultHandler, self).__init__()
#        self.result_handlers = set()
#        for rh in result_handlers:
#            handler = {
#                SetResultHandler: self.set_result,
#                LogResultHandler: self.log_result,
#                PrintResultHandler: self.print_result
#            }.get(rh)
#            self.result_handlers.add(handler)
#            
#
#    def log_result(self, predicted_class, actual_class=None, features=None, confidence=None):
#        
#        """
#        Save the results of the decoder, HSD parameters, and raw data used
#        to a file.
#        """
#        log = dict(
#            targets=self.targets,
#            fs=self.fs,
#            nfft=self.nfft,
#            n_harmonics=self.n_harmonics,
#            selected_channels=self.selected_channels,
#            data=self.model.get_data(),
#            predicted_class=predicted_class,
#            actual_class=actual_class,
#            features=features,
#            confidence=confidence
#        )
#        np.savetxt(self.file_handle, log, fmt='%d', delimiter='\t')
#        #np.savez("%s-%d" % (self.label, time.time()), **log)
#
#    def print_result(self, predicted_class, actual_class=None, features=None, confidence=None):
#        
#    
#
#        
#    def decode(self, command):
#        """
#        Buffer incoming data samples from the command object, then determine if
#        a decision has been reached and handle accordingly.
#        Must return the command object with or without modification.
#        """
#        self.model.check_state()
#        
#        if command.is_valid():
#            self.model.buffer_data(command.matrix[:, 0:self.n_electrodes])
#            
#        if self.model.is_ready():
#            scores = self.extract_features(self.model.get_data())
#            result = self.dodecode(scores)
#            
#            if result is None:
#                predicted_class = None
#                confidence = 1.0
#            else:
#                predicted_class = result[0]
#                confidence = result[1]
#                
#            for handler in self.result_handlers:
#                handler(predicted_class, command=command, features=scores,
#                        actual_class=self.actual_class, confidence=confidence)
#            self.model.handle_result(result)
#            
#            self.result_handler.handle_result(result) #
#            
#        return command
#            
#            