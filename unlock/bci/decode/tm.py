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
import numpy as np
import scipy.signal as sig

from unlock.bci.decode.decode import UnlockDecoder


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
    def __init__(self, n_electrodes=8, selected_channels=None,
                 reference_channel=None):
        super(TemplateFeatureExtractor, self).__init__()

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
        y = command.buffered_data[:]
        y -= np.mean(y, axis=0)
        if self.reference_channel is not None:
            y -= y[:, [self.reference_channel]]
        y = y[:, self.selected_channels]
        y = np.mean(y, axis=1)

        command.features = y
        return command
        
        
class ScoredTemplateMatch(UnlockDecoder):
    def __init__(self, templates, threshold_decoder):
        super(ScoredTemplateMatch, self).__init__()
        self.templates = templates
        self.threshold_decoder = threshold_decoder
        
    def decode(self, command):
        """
        Find the largest frequency magnitude and determine if it meets
        threshold criteria.
        """
        scores = np.zeros(1)
        if self.templates is not None:
            scores = np.dot(command.features, self.templates)
        # TODO: rethink "features" vs "scores" for thresholding
        command.features = scores
        command.winner = np.argmax(command.features)
        command = self.threshold_decoder.decode(command)

        result_string = None
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


class MsequenceTemplateMatcher(UnlockDecoder):
    def __init__(self, templates, n_electrodes=8, center=2, surround=(0, 4, 7),
                 alpha=0.05, trial_marker=1, buffer_size=1000, training=False):
        super(MsequenceTemplateMatcher, self).__init__()
        self.filename = templates
        self.templates = []
        self.n_electrodes = n_electrodes
        self.center = center
        self.surround = surround
        self.alpha = alpha
        self.mu = np.zeros(n_electrodes)
        self.trial_marker = trial_marker
        self.downsample = [64, 64, 64]

        self.channels = list(range(n_electrodes)) + [10]
        self.buffer = np.zeros((buffer_size, n_electrodes))
        self.cursor = 0
        self.decode_now = False
        self.last_event = None

        self.training = training
        self.updating = not training
        self.n_targets = 5
        self.training_buffer = [
            np.zeros((5, 30, 64, self.n_electrodes)),
            np.zeros((5, 30, 64, self.n_electrodes)),
            np.zeros((3, 30, 64, self.n_electrodes))
        ]
        self.template_features = [
            np.zeros((4, 30, 64)),
            np.zeros((4, 30, 64)),
            np.zeros((2, 30, 64))
        ]
        self.baselines = np.zeros((3, 64, self.n_electrodes))
        self.mmads = np.zeros(4)
        self.trial_idx = np.zeros(self.n_targets, dtype=np.int32)
        self.target_idx = 0
        self.template_idx = 0

        if self.training:
            self.templates.append(np.zeros((4, 64)))
            self.templates.append(np.zeros((4, 64)))
            self.templates.append(np.zeros((2, 64)))
            self.initial_templates = []
        else:
            try:
                self.templates = np.load(self.filename)['templates']
            except IOError:
                raise Exception("Missing template file!")

    def decode(self, command):
        if self.decode_now:
            trial = sig.resample(self.buffer[0:self.cursor], self.downsample[self.template_idx], axis=0)
            features = self.extract_features(trial)
            command = self.classify(command, features)
            self.decode_now = False
            self.cursor = 0
            return command

        if not command.is_valid() or not self.started:
            return command

        data = command.matrix[:, self.channels]
        event = None
        for d in data:
            marker = d[-1]
            if marker == self.trial_marker:
                event = self.cursor

            sample = d[0:self.n_electrodes]
            self.mu = (1-self.alpha) * self.mu + self.alpha * sample
            self.buffer[self.cursor] = sample - self.mu
            self.cursor += 1

        if event is None:
            return command
        self.last_event = event

        if 480 < event < 525:
            trial = sig.resample(self.buffer[0:self.last_event], self.downsample[self.template_idx], axis=0)
            if self.training:
                self.training_buffer[self.template_idx][self.target_idx, self.trial_idx[self.target_idx]] = trial
                self.trial_idx[self.target_idx] += 1

                if self.updating and self.target_idx != len(self.trial_idx)-1:
                    feature = self.extract_features(trial - self.baselines[self.template_idx])
                    self.template_features[self.template_idx][self.target_idx, self.trial_idx[self.target_idx]-1] = feature
                    features = self.template_features[self.template_idx][self.target_idx, 0:self.trial_idx[self.target_idx]]
                    template = np.median(features, axis=0)
                    mmad = np.mean(np.median(np.abs(features - template), axis=0))
                    score = 1/(1+np.exp(10*(mmad-0.5)))
                    scores = np.zeros(5)
                    scores[self.target_idx] = score
                    command.decoder_scores = scores
                    if mmad < self.mmads[self.target_idx]:
                        self.mmads[self.target_idx] = mmad
                        self.templates[self.template_idx][self.target_idx] = template

            else:
                features = self.extract_features(trial)
                command = self.classify(command, features)

        self.buffer = np.roll(self.buffer, -self.last_event, axis=0)
        self.cursor -= self.last_event

        return command

    def classify(self, command, features):
        scores = np.corrcoef(self.templates[self.template_idx], features)[self.n_targets, 0:self.n_targets]
        predict = np.argmax(scores)
        print(self.last_event, self.target_idx, predict, scores)

        command.decoder_scores = scores
        if scores[predict] > 0.3:
            command.decision = predict + 1

        return command

    def extract_features(self, trial):
        features = (np.sum(trial[:, self.surround], axis=1) -
                 len(self.surround)*trial[:, self.center])
        return features

    def start(self):
        super(MsequenceTemplateMatcher, self).start()
        self.cursor = 0
        self.decode_now = False
        self.last_event = None

    def stop(self):
        super(MsequenceTemplateMatcher, self).stop()
        if not self.training and self.cursor > 480 and self.last_event is not None:
            self.decode_now = True

    def save_templates(self):
        if not self.updating:
            if self.trial_idx[0] == 0:
                return
            self.baselines[self.template_idx] = np.median(self.training_buffer[self.template_idx][-1, 0:10], axis=0)
            for i in range(self.n_targets - 1):
                n_trials = self.trial_idx[i]
                trials = self.training_buffer[self.template_idx][i] - self.baselines[self.template_idx]
                features = np.sum(trials[0:n_trials, :, [0, 4, 7]], axis=2) - 3*trials[0:n_trials, :, 2]
                self.template_features[self.template_idx][i, 0:n_trials] = features
                template = np.median(features, axis=0)
                self.templates[self.template_idx][i] = template
                self.mmads[i] = np.mean(np.median(np.abs(features - template), axis=0))
        np.savez(self.filename, templates=self.templates, template_features=self.template_features,
                 training_buffer=self.training_buffer)

    def set_block(self, block_idx):
        # TODO: perform channel analysis to determine ideal filter for generating template
        self.template_idx = block_idx
        self.n_targets = len(self.training_buffer[self.template_idx])
        self.trial_idx = np.zeros(self.n_targets, dtype=np.int32)
        self.mmads = np.zeros(self.n_targets)

