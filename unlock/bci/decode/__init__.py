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
import numpy as np

from unlock.bci.decode.decode import *
from unlock.bci.decode.harmonic import *
from unlock.bci.decode.femg import *
from unlock.bci.decode.eyeblink import *
from unlock.bci.decode.tm import *

    
class UnlockDecoderFactory(object):
    def create_decoder(self, decoder, **kwargs):
        func = {
            'harmonic_sum': self.create_harmonic_sum_decision,
            'template_match': self.create_template_match,
            'eyeblink_detector': self.create_eyeblink_detector,
            'facial_emg': self.create_facial_emg_detector,
            'sliding': self.create_sliding,
            'fixed_time': self.create_fixed_time_buffering,
            'absolute': self.create_absolute_threshold,
            'lda': self.create_lda_threshold,
            'offline': self.create_offline_trial_data,
            'unknown': self.unknown
        }.get(decoder, self.unknown)
        if func is None:
            raise Exception("Undefined Decoder: "+str(decoder)+" kwargs = "+str(kwargs))
        return func(**kwargs)
        
    def create_harmonic_sum_decision(self, buffering_decoder=None,
            threshold_decoder=None, selector=None, fs=256, n_electrodes=8,
            targets=(12.0, 13.0, 14.0, 15.0), nfft=2048, target_window=0.1,
            n_harmonics=1, selected_channels=None):
        assert buffering_decoder and threshold_decoder

        trial_state_decoder = TrialStateControlledDecoder(None)
        feature_extractor = HarmonicFeatureExtractor(fs=fs, nfft=nfft,
            targets=targets, n_electrodes=n_electrodes,
            target_window=target_window, n_harmonics=n_harmonics,
            selected_channels=selected_channels)
        decider = ScoredHarmonicSumDecision(threshold_decoder, targets)

        decoder_chain = UnlockDecoderChain()
        if selector is not None:
            decoder_chain.add(selector)
        decoder_chain.add(trial_state_decoder)
        decoder_chain.add(buffering_decoder)
        decoder_chain.add(feature_extractor)
        decoder_chain.add(decider)

        return decoder_chain

    def create_template_match(self, templates=None, buffering_decoder=None,
                              threshold_decoder=None, n_electrodes=8,
                              selected_channels=None, reference_channel=None):
        assert buffering_decoder and threshold_decoder
        trial_state_decoder = VepTrainerStateControlledDecoder(None)
        feature_extractor = TemplateFeatureExtractor(n_electrodes,
                                                     selected_channels,
                                                     reference_channel)
        decider = ScoredTemplateMatch(templates, threshold_decoder)
        logger = OfflineTrialDataDecoder('tm')

        decoder_chain = UnlockDecoderChain()
        decoder_chain.add(trial_state_decoder)
        decoder_chain.add(buffering_decoder)
        decoder_chain.add(feature_extractor)
        decoder_chain.add(decider)
        decoder_chain.add(logger)

        return decoder_chain

    def create_offline_vep_trial_recorder(
            self, buffering_decoder=None, label='trial'):
        trial_state_decoder = VepTrainerStateControlledDecoder(None)
        logger = OfflineTrialDataDecoder(label)

        decoder_chain = UnlockDecoderChain()
        decoder_chain.add(trial_state_decoder)
        decoder_chain.add(buffering_decoder)
        decoder_chain.add(logger)

        return decoder_chain

    def create_offline_trial_data(self, label='trial'):
        return OfflineTrialDataDecoder(label)

    def create_fixed_time_buffering(self, electrodes=8, window_length=768):
        return FixedTimeBufferingDecoder(electrodes, window_length)
    
    def create_sliding(self, electrodes=8, step_size=32, trial_limit=768):
        return SlidingWindowDecoder(electrodes, step_size, trial_limit)
    
    def create_absolute_threshold(self, threshold=0, reduction_fn=np.mean):
        return AbsoluteThresholdDecoder(threshold, reduction_fn)
        
    def create_lda_threshold(self, x=(0, 1), y=(0, 1), min_confidence=0.5, reduction_fn='np.mean'):
        return LdaThresholdDecoder(x, y, min_confidence, reduction_fn)
        
    def create_eyeblink_detector(self, eog_channels=(7,), strategy='length',
                                 rms_threshold=0):
        return EyeBlinkDetector(eog_channels, strategy, rms_threshold)
        
    def create_facial_emg_detector(self):
        return None
        
    def unknown(self, **kwargs):
        raise("Unsupported")
