# Copyright (c) James Percent and Unlock contributors.
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

__author__ = 'jpercent'


class Filter(object):
    def apply(self, matrix):
        '''Returns the filtered data'''
        return matrix


class InplaceFilter(Filter):
    def apply(self, matrix):
        '''Imperatively applies the filter to the data; returns None'''
        return None


class MobilabRawDataToMilliVoltsFilter(Filter):
    def __init__(self, channel_sensitivity=500):
        self.channel_sensitivity = channel_sensitivity
        self.resolution_factor = (10 /2**18) * self.channel_sensitivity
        self.micro_to_millis_factor = 1000

    def apply(self, matrix):
        matrix *= self.resolution_factor * self.micro_to_millis_factor


class OtherMobilabData(Filter):
    def __init__(self, sampling_hz=256, high_pass_filter_bound=0.5, low_pass_filter_bound=100):
        self.sampling_hz = sampling_hz
        self.high_pass = high_pass_filter_bound
        self.low_pass = low_pass_filter_bound


# notes from andres; he sent a follow up email that says the channel
#
#                 Fs               = 256;                                % Sampling frequency
#chSensit      = 500/1000;                        % channel sensitivity is 500 microvolts, passing from micro to millivolts
#filtHigh          = 0.5;                                % high pass bound for filter
#filtLow           = 100;                               % low pass bound for filter
#resolutFactor = (2*5/(2^16*4))*(chSensit); % resolution factor to multiply raw data to get it in millivolts
#The data read by unlock is then multiplied by the resolution factor (resolutFactor):
#unlockData.data     = rawData*resolutFactor*1000;         % This gives data in milliVolts, how it is usually

#I dug deeper into the matter of the format of the recorded data to be output in millivolt values and realized I was
# dividing by an extra 1000 value in the formula. The channel sensitivity I gave you yesterday was 500/1000 but it
# should be in reality 500. This means the 1000 should be removed.