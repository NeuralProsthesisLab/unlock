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

from unlock.decode.classify.classify import UnlockClassifier
from unlock.util import TrialState
import numpy as np
from sklearn import lda
import time


class HarmonicSumDecision(UnlockClassifier):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, task_state=None, targets=(12.0, 13.0, 14.0, 15.0),
                 duration=3, fs=500, electrodes=8, filters=None):
        assert task_state is not None
        super(HarmonicSumDecision, self).__init__(task_state)
        self.targets = targets
        self.target_window = 0.1
        self.fs = fs
        self.electrodes = electrodes
        self.n_samples = int(duration * fs)
        self.overflow = 256
        self.buffer = np.zeros((self.n_samples + self.overflow, electrodes))
        self.cursor = 0
        self.filters = filters

        self.enabled = True

        self.fft_params()

    def fft_params(self):
        """Determine all the relevant parameters for fft analysis"""
        i = 2
        while i <= self.n_samples:
            i *= 2
        self.nfft = i
        self.window = 1 #np.hanning(self.nSamples).reshape((self.nSamples, 1))
        self.nfft = 2048

        # indices for frequency components
        # as the values returned by the fft are in freq space, the resolution
        # is limited to the size of the fft, which in this case is just the
        # next largest power of 2. for a small time window, this results in
        # poor frequency resolution.
        self.nHarmonics = 2
        self.harmonics = []
        f = np.fft.fftfreq(self.nfft, 1.0/self.fs)[0:self.nfft/2]
        f_step = f[1]
        for target in self.targets:
            r = []
            for h in range(1, self.nHarmonics+1):
                q = h * target / f_step
                # q = np.where(np.logical_and(f > h*target - self.target_window,
                #                             f < h*target + self.target_window))
                r.extend([np.floor(q), np.ceil(q)])
            self.harmonics.append(r)

    def classify(self, command):
        """
        command contains a data matrix of samples assumed to be an ndarray of
         shape (samples, electrodes+)
        """
        classify_now = False
        if self.task_state.last_change == TrialState.RestExpiry:
            self.enabled = True
            self.cursor = 0
        elif self.task_state.last_change == TrialState.TrialExpiry:
            self.enabled = False
            if self.cursor >= 0.9*self.n_samples:
                classify_now = True
        elif not self.enabled or not command.is_valid():
            return command

        # this check is a hack to deal with the edge case when the task period
        # expires and we want to classify now but we also have an invalid
        # data command. TODO: find a less ugly way to handle this
        if command.is_valid():
            samples = command.matrix[:, 0:self.electrodes]
            s = samples.shape[0]
            self.buffer[self.cursor:self.cursor+s, :] = samples
            self.cursor += s

        if self.cursor >= self.n_samples or classify_now:
            x = self.buffer[0:self.cursor]
            #if self.filters is not None:
            #    x = self.filters.apply(x)
            x = x[:, 1:4]# - x[:, 6].reshape((len(x), 1))
            x -= np.mean(x, axis=0)
            y = np.abs(np.fft.rfft(self.window * x, n=self.nfft, axis=0))
            sums = np.zeros(len(self.targets))
            for i in range(len(self.targets)):
                sums[i] = np.sum(y[self.harmonics[i], :])
            d = np.argmax(sums)
            np.set_printoptions(precision=2)
            print("HSD: %d (%.1f Hz)" % (d+1, self.targets[d]),
                sums / np.max(sums), self.cursor)
            ## TODO: roll any leftover samples to the beginning of the buffer
            self.cursor = 0
            command.decision = d + 1
            
        return command


class HarmonicSumDecisionDiagnostic(UnlockClassifier):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, targets=(12.0, 13.0, 14.0, 15.0),
                 duration=3, fs=500, electrodes=8, filters=None, label='HSD'):
        super(HarmonicSumDecisionDiagnostic, self).__init__()
        self.targets = targets
        self.target_window = 0.1
        self.fs = fs
        self.electrodes = electrodes
        self.n_samples = int(duration * fs)
        self.overflow = 256
        self.buffer = np.zeros((self.n_samples + self.overflow, electrodes))
        self.cursor = 0
        self.filters = filters
        self.label = label

        self.enabled = True
        self.classify_now = False
        self.target_label = None

        self.fft_params()

    def fft_params(self):
        """Determine all the relevant parameters for fft analysis"""
        i = 2
        while i <= self.n_samples:
            i *= 2
        self.nfft = i
        self.window = 1 #np.hanning(self.nSamples).reshape((self.nSamples, 1))
        self.nfft = 2048

        # indices for frequency components
        # as the values returned by the fft are in freq space, the resolution
        # is limited to the size of the fft, which in this case is just the
        # next largest power of 2. for a small time window, this results in
        # poor frequency resolution.
        self.nHarmonics = 2
        self.harmonics = []
        f = np.fft.fftfreq(self.nfft, 1.0/self.fs)[0:self.nfft/2]
        f_step = f[1]
        for target in self.targets:
            r = []
            for h in range(1, self.nHarmonics+1):
                q = h * target / f_step
                # q = np.where(np.logical_and(f > h*target - self.target_window,
                #                             f < h*target + self.target_window))
                r.extend([np.floor(q), np.ceil(q)])
            self.harmonics.append(r)

    def start(self):
        self.enabled = True
        self.cursor = 0
        self.classify_now = False

    def stop(self):
        self.enabled = False
        if self.cursor >= 0.9*self.n_samples:
            self.classify_now = True

    def classify(self, command):
        """
        command contains a data matrix of samples assumed to be an ndarray of
         shape (samples, electrodes+)
        """
        if self.classify_now:
            return self.decode()

        if not self.enabled or not command.is_valid():
            return

        samples = command.matrix[:, 0:self.electrodes]
        s = samples.shape[0]
        self.buffer[self.cursor:self.cursor+s, :] = samples
        self.cursor += s

        if self.cursor >= self.n_samples:
            return self.decode()

    def decode(self):
        log = {
            'targets': self.targets,
            'fs': self.fs,
            'n_samples': self.n_samples,
            'nfft': self.nfft,
            'n_harmonics': self.nHarmonics,
            'feature_width': 2,
            'channel_weights': [0, 1, 1, 1, 0, 0, 0, 0],
            'feature_method': 'fft',
            'classify_method': 'argmax of sums',
        }
        x = self.buffer[0:self.cursor]
        log['data'] = x
        #if self.filters is not None:
        #    x = self.filters.apply(x)
        x = x[:, 1:4]  # - x[:, 6].reshape((len(x), 1))
        x -= np.mean(x, axis=0)
        y = np.abs(np.fft.rfft(self.window * x, n=self.nfft, axis=0))
        sums = np.zeros(len(self.targets))
        for i in range(len(self.targets)):
            sums[i] = np.sum(y[self.harmonics[i], :])
        log['sums'] = sums
        d = np.argmax(sums)
        log['class_label'] = d
        if self.target_label is not None:
            log['target_label'] = self.target_label
        np.set_printoptions(precision=2)
        print("%s: %d (%.1f Hz)" % (self.label, d+1, self.targets[d]),
            sums / np.max(sums), self.cursor)
        ## TODO: roll any leftover samples to the beginning of the buffer
        self.cursor = 0
        self.classify_now = False
        np.savez("%s-%d" % (self.label, time.time()), **log)
        #command.decision = d + 1
        return "%s: %.1f Hz" % (self.label, self.targets[d])


###############################################################################
# New Harmonic Sum Decision Decoder
###############################################################################
SetResultHandler = 0
LogResultHandler = 1
PrintResultHandler = 2


class NewHarmonicSumDecision(UnlockClassifier):
    """
    Harmonic Sum Decision (HSD) computes the frequency power spectrum of EEG
    data over one or more electrodes then sums the amplitudes of target
    frequencies and their harmonics. The target with the highest sum is chosen
    as the attended frequency.
    """
    def __init__(self, model, threshold_strategy, fs=256, n_electrodes=8,
                 result_handlers=(), targets=(12.0, 13.0, 14.0, 15.0),
                 target_window=0.1, nfft=2048, n_harmonics=1,
                 selected_channels=None, label='HSD', **kwargs):
        super(NewHarmonicSumDecision, self).__init__()

        self.model = model
        self.threshold_strategy = threshold_strategy

        self.fs = fs
        self.n_electrodes = n_electrodes
        self.targets = targets
        self.target_window = target_window
        self.nfft = nfft
        self.n_harmonics = n_harmonics
        self.label = label

        self.selected_channels = selected_channels
        if selected_channels is None:
            self.selected_channels = range(self.n_electrodes)

        self.result_handlers = set()
        for rh in result_handlers:
            handler = {
                SetResultHandler: self.set_result,
                LogResultHandler: self.log_result,
                PrintResultHandler: self.print_result
            }.get(rh)
            self.result_handlers.add(handler)

        self.actual_class = None
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

    def start(self):
        self.model.start()

    def stop(self):
        self.model.stop()

    def extract_features(self, x):
        """
        The features used by HSD are the summed magnitudes of one or more
        harmonics of the target frequencies across one or more channels of
        recorded data.
        """
        y = x[:, self.selected_channels]
        y -= np.mean(y, axis=0)
        y = np.abs(np.fft.rfft(y, n=self.nfft, axis=0))
        scores = np.zeros(len(self.targets))
        for i in range(len(self.targets)):
            score = 0
            for harmonic in self.harmonics[i]:
                score += np.mean(y[harmonic, :])
            scores[i] = score
        return scores

    def decode(self, scores):
        """
        Find the largest frequency magnitude and determine if it meets
        threshold criteria.
        """
        sort = np.sort(scores)[::-1]
        winner = np.argmax(scores)
        accept, confidence = self.threshold_strategy.evaluate(sort[0:2])

        if accept:
            return winner, confidence

    def classify(self, command):
        """
        Buffer incoming data samples from the command object, then determine if
        a decision has been reached and handle accordingly.
        Must return the command object with or without modification.
        """

        if command.is_valid():
            self.model.buffer_data(command.matrix[:, 0:self.n_electrodes])

        if self.model.is_ready():
            scores = self.extract_features(self.model.get_data())
            result = self.decode(scores)

            if result is not None:
                predicted_class = result[0]
                confidence = result[1]
                for handler in self.result_handlers:
                    handler(predicted_class, features=scores,
                            actual_class=self.actual_class,
                            confidence=confidence, command=command)

            self.model.handle_result(result)

        return command

    def set_result(self, predicted_class, command=None, **kwargs):
        """
        Pass the result of the classifier on to the command object to perform
        a system action.
        """
        if command is not None:
            command.decision = predicted_class

    def log_result(self, predicted_class, actual_class=None, features=None,
                   confidence=None, **kwargs):
        """
        Save the results of the classifier, HSD parameters, and raw data used
        to a file.
        """
        log = dict(
            targets=self.targets,
            fs=self.fs,
            nfft=self.nfft,
            n_harmonics=self.n_harmonics,
            selected_channels=self.selected_channels,
            data=self.model.get_data(),
            predicted_class=predicted_class,
            actual_class=actual_class,
            features=features,
            confidence=confidence
        )
        np.savez("%s-%d" % (self.label, time.time()), **log)

    def print_result(self, predicted_class, actual_class=None, features=None,
                     confidence=None, **kwargs):
        """
        Print the results of the HSD decoder to the console.
        """
        np.set_printoptions(precision=2)
        result = "%s: %d (%.1f Hz)" % (self.label, predicted_class,
                                       self.targets[predicted_class])
        if confidence is not None:
            result = "%s [%.2f]" % (result, confidence)

        if actual_class is not None:
            result = "%s / %d (%.1f Hz)" % (result, actual_class,
                                            self.targets[actual_class])
        print(result)
        if features is not None:
            print(features)


###############################################################################
# Decoder States
###############################################################################
FixedTimeDecoder = 0
ContinuousDecoder = 1


def new_decoder_model(decoder, buffer_shape, **kwargs):
    """Decoder State Factory"""
    if decoder == FixedTimeDecoder:
        return FixedTimeDecoderModel(buffer_shape, **kwargs)
    elif decoder == ContinuousDecoder:
        return ContinuousDecoderModel(buffer_shape, **kwargs)
    else:
        raise NotImplementedError("HSD decoder type not implemented")


class DecoderModel(object):
    def __init__(self, buffer_shape, **kwargs):
        self.buffer = np.zeros(buffer_shape)
        self.cursor = 0
        self.enabled = True

    def start(self):
        """Start and initialize the decoder to accept data."""
        self.enabled = True
        self.cursor = 0

    def stop(self):
        """Stop the decoder from accepting new data."""
        self.enabled = False

    def buffer_data(self, data):
        """
        Determines how to buffer incoming data samples. By default, samples
        are added from the beginning of the buffer until it is full, then
        further samples cause the early samples to be discarded.
        data is assumed to have a shape of (n_samples, n_channels)
        """
        if not self.enabled:
            return

        n_samples = data.shape[0]
        if self.cursor + n_samples >= self.buffer.shape[0]:
            shift = self.cursor + n_samples - self.buffer.shape[0]
            self.buffer = np.roll(self.buffer, -shift, axis=0)
            self.buffer[-n_samples:] = data
            self.cursor = self.buffer.shape[0]
        else:
            self.buffer[self.cursor:self.cursor+n_samples] = data
            self.cursor += n_samples

    def get_data(self):
        """
        Returns the buffered data according to the cursor position.
        """
        return self.buffer[0:self.cursor]

    def is_ready(self):
        """
        Returns a boolean indicating whether or not to run the decoder on the
        accumulated data.
        """
        raise NotImplementedError

    def handle_result(self, result):
        """
        Any state updates or actions that are required after the decoder has
        run.
        """
        raise NotImplementedError


class FixedTimeDecoderModel(DecoderModel):
    def __init__(self, buffer_shape, window_length, **kwargs):
        super(FixedTimeDecoderModel, self).__init__(buffer_shape)
        self.window_length = window_length
        self.decode_now = False

    def stop(self):
        self.enabled = False
        if self.cursor >= 0.9*self.window_length:
            self.decode_now = True

    def is_ready(self):
        return self.cursor >= self.window_length or self.decode_now

    def handle_result(self, result):
        self.decode_now = False
        self.cursor = 0


class ContinuousDecoderModel(DecoderModel):
    def __init__(self, buffer_shape, step_size, trial_limit=1, **kwargs):
        super(ContinuousDecoderModel, self).__init__(buffer_shape)
        self.step_size = step_size
        self.trial_limit = trial_limit
        self.last_mark = 0

    def is_ready(self):
        return self.cursor >= self.last_mark + self.step_size

    def handle_result(self, result):
        if result is not None or self.cursor >= self.trial_limit:
            self.last_mark = 0
            self.cursor = 0
        else:
            self.last_mark = self.cursor + self.step_size


###############################################################################
# Threshold Strategies
###############################################################################
NoThreshold = 0
AbsoluteThreshold = 1
LDAThreshold = 2


def new_threshold_strategy(strategy, **kwargs):
    """Threshold Strategy Factory"""
    if strategy == NoThreshold:
        return NoThresholdStrategy()
    elif strategy == AbsoluteThreshold:
        return AbsoluteThresholdStrategy(**kwargs)
    elif strategy == LDAThreshold:
        return LDAThresholdStrategy(**kwargs)
    else:
        raise NotImplementedError("HSD threshold strategy not implemented")


class ThresholdStrategy(object):
    def evaluate(self, sample):
        """
        Returns whether or not the provided sample passes a threshold test and
        the associated confidence of that decision.
        """
        raise NotImplementedError


class NoThresholdStrategy(ThresholdStrategy):
    """Accepts everything"""
    def evaluate(self, sample):
        return True, 1.0


class AbsoluteThresholdStrategy(ThresholdStrategy):
    """Accepts everything greater than or equal to a set value."""
    def __init__(self, threshold=0, reduction_fcn=np.mean, **kwargs):
        self.threshold = threshold
        self.reduction_fcn = reduction_fcn

    def evaluate(self, sample):
        return self.reduction_fcn(sample) >= self.threshold, 1.0


class LDAThresholdStrategy(ThresholdStrategy):
    """
    Uses an LDA classifier to determine the threshold boundary. LDA predictions
    above a provided confidence level are accepted. Training data must be
    supplied to the classifier.
    """
    def __init__(self, x=(0, 1), y=(0, 1), min_confidence=0.5,
                 reduction_fcn=np.mean, **kwargs):
        self.min_confidence = min_confidence
        self.clf = lda.LDA()
        self.clf.fit(x, y)
        self.reduction_fcn = reduction_fcn

    def evaluate(self, sample):
        confidence = self.clf.predict_proba(self.reduction_fcn(sample))[0, 1]
        return confidence >= self.min_confidence, confidence


###############################################################################
# Global Creation Method
###############################################################################
def new_hsd(decoder_type, strategy_type, **kwargs):
    """HSD Decoder Factory"""

    ## NOTE: model/strategy objects should be created elsewhere to avoid having
    ## an unwiedly kwargs list being passed around to everyone.
    fs = kwargs.get('fs', 256)
    trial_length = kwargs.get('trial_length', 3)
    n_electrodes = kwargs.get('n_electrodes', 8)
    buffer_shape = (fs * (trial_length + 1), n_electrodes)
    result_handlers = kwargs.get('result_handlers', (PrintResultHandler,))

    kwargs['fs'] = fs
    kwargs['trial_length'] = trial_length
    kwargs['n_electrodes'] = n_electrodes
    kwargs['result_handlers'] = result_handlers

    decoder_state = new_decoder_model(decoder_type, buffer_shape, **kwargs)
    threshold_strategy = new_threshold_strategy(strategy_type, **kwargs)
    return NewHarmonicSumDecision(decoder_state, threshold_strategy, **kwargs)