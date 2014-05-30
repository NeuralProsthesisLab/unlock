# Copyright (c) Byron Galbraith and Unlock contributors.
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


class TemplateFeatureExtractor(UnlockDecoder):
    """
    Template Matching (TM) creates templates from broad-spectrum signals that
    align with a given stimulus. New signals are then scored against the
    templates, with the highest scoring template selected as the attended
    stimulus.
    """
    def __init__(self, templates, fs=256, n_electrodes=8,
                 selected_channels=None, reference_channel=None):
        super(TemplateFeatureExtractor, self).__init__()

        self.templates = templates
        self.fs = fs
        self.n_electrodes = n_electrodes

        self.selected_channels = selected_channels
        if not selected_channels:
            self.selected_channels = range(self.n_electrodes)
        self.reference_channel = reference_channel

        self.file_handle = None
        self.output_file_prefix = 'template_feature_extractor'

    def decode(self, command):
        """
        The feature used by template matching is the filtered and averaged
        signal over a single presentation.
        """
        # TODO: this step should be replaced with a passed in filter chain
        y = command.matrix[:, self.selected_channels]
        if self.reference_channel is not None:
            y -= command.matrix[:, [self.reference_channel]]
        y -= np.mean(y, axis=0)

        command.scores = np.dot(y, self.templates)

        return command
        
        
class ScoredTemplateMatch(UnlockDecoder):
    def __init__(self, threshold_decoder):
        super(ScoredTemplateMatch, self).__init__()
        self.threshold_decoder = threshold_decoder
        
    def decode(self, command):
        """
        Find the largest frequency magnitude and determine if it meets
        threshold criteria.
        """
        assert hasattr(command, 'scores')
        result_string = None

        command.winner = np.argmax(command.scores)
        command = self.threshold_decoder.decode(command)
            
        if command.accept:
            command.class_label = command.winner
            np.set_printoptions(precision=2)
            print('Command class label ', command.class_label)
            result_string = "ScoredTemplateMatch: %d" % command.class_label
                
            if command.confidence:
                result_string = "%s [%.2f]" % (result_string, command.confidence)
                
        else:
            command.class_label = -1
            result_string = "ScoredTemplateMatch: could not make a decision"

        if result_string:
            print(result_string)

        return command