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
import traceback
import sys

SetResultHandler = 0
LogResultHandler = 1
PrintResultHandler = 2


class HarmonicFeatureExtractor(UnlockDecoder):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, fs=256, n_electrodes=8, target_window=0.1, nfft=2048,
                 targets=(12.0, 13.0, 14.0, 15.0), n_harmonics=1,
                 selected_channels=None):
        super(HarmonicFeatureExtractor, self).__init__()
        self.fs = fs
        self.n_electrodes = n_electrodes
        self.targets = targets
        self.target_window = target_window
        self.nfft = nfft
        self.n_harmonics = n_harmonics
        
        self.selected_channels = selected_channels
        if not selected_channels:
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
        self.output_file_prefix = 'hsd_feature_extractor'

    def decode(self, command):
        """
        The features used by harmonic sum decision are the summed magnitudes of
        one or more harmonics of the target frequencies across one or more
        channels of recorded data.
        """
        assert hasattr(command, "buffered_data")
        y = command.buffered_data[:, self.selected_channels]
        y -= np.mean(y, axis=0)
        y = np.abs(np.fft.rfft(y, n=self.nfft, axis=0))

        scores = np.zeros(len(self.targets))
        for i in range(len(self.targets)):
            score = 0
            for harmonic in self.harmonics[i]:
                score += np.mean(y[harmonic, :])
            scores[i] = score
        command.features = scores
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
        assert hasattr(command, 'features')
        result_string = None

        command.winner = np.argmax(command.features)
        command = self.threshold_decoder.decode(command)
            
        if command.accept:
            command.decision = command.winner + 1
            command.class_label = command.winner
            np.set_printoptions(precision=2)
            print("Targets ", self.targets, ' command classlabel ',
                  command.class_label)
            result_string = "ScoredHarmonicSumDecision: %d (%.1f Hz)" % \
                            (command.class_label,
                             self.targets[command.class_label])
                
            if command.confidence:
                result_string = "%s [%.2f]" % (result_string,
                                               command.confidence)
        else:
            command.class_label = -1
            result_string = "ScoredHarmonicSumDecision: could not make a decision"

        if result_string:
            print(result_string)

        return command
