function  [filtParams] = setFilterParams(freqBand,filterType,filterOrder,smpRate)
% function [filtParams] = setFilterParams(freqBand,filterType,filterOrder,smpRate)
%
% Sets up filter parameters for generating band-filtered signals.
%
% INPUT
% freqBands:    [low,high]-pass frequencies of each frequency pass-band to extract from continuous channels
% filterType:   Name of filter to use
% filterOrder:  Order of filter to use
% smpRate:      Sampling rate (hz) of signal to be filtered
%
% OUTPUT
% filtParams:   Parameters for band-pass filtering, to be used in b,a form with filter() or filtfilt(),
%               for each given frequency band returned in a struct array
%
% Author:       Andres; adapted from Scott's and Mike's setContFilterParams code

% Vbles
nF = size(freqBand,1);
FNyquist = smpRate/2;
freqNorm  = freqBand/FNyquist;         % Normalized filter cutoff frequencies

% Checking lower freq. cut is lower than hi-bound
if freqNorm(1) > freqNorm(2), error('Lower cut frequency bound higher than high cut bound: [%i-%i]',freqNorm), return, end

% Get filter params
switch filterType
    case 'butter';
        % Low-pass filter (lo-cut frequency = 0) and high-cut frequency < Nyquist Freq.
        if (freqNorm(1) == 0) && (freqNorm(2) < 1)
            [filtParams.b,filtParams.a] = butter(filterOrder, freqNorm(2), 'low');
            
            % High-pass filter (hi-cut frequency = FNyquist (or inf)) and low-cut frequency ~= 0
        elseif ((freqNorm(2) == 1) || isinf(freqNorm(2))) && (freqNorm(1) > 0)
            [filtParams.b,filtParams.a] = butter(filterOrder, freqNorm(1), 'high');
            
            % Low-cut frequency = Nyquist, hi-cut frequency = 0. Do not filter.
        elseif (freqNorm(1) == 0) && (freqNorm(2) == 1)
            filtParams.b = [1 zeros(1,filterOrder)];      % transfer function equals 1
            filtParams.a = [1 zeros(1,filterOrder)];      % transfer function equals 1
            
            % Band-pass filtering
        else
            [filtParams.b,filtParams.a] = butter(filterOrder, freqNorm);
        end
    otherwise;
        error('setFilterParams: Filter type %s unknown',filterType);
end
