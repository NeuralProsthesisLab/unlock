function unlockInfo = setUnlockParams(unlockInfo)
%
%
%
%
%
%
%
% Author:       Andres 
% Created:      v1. 02 Jan 2014 
% Las modified: v1. 02 Jan 2014

%% Main Params
unlockInfo.main.nCols           = 12;                   % total number of channels 
unlockInfo.main.nChs            = 8;                    % Number of EEG leads and extra channels (EMG, EOG, triggers)
unlockInfo.main.endTrialFlag 	= -1;                   % flag used to signal end of trial (when decoder makes a decision)
unlockInfo.main.triggeredData   = true;                 % logical. True if each trial has a trigger so fromEnd or fromStart are not required for epoching. 

%% Filter params
unlockInfo.main.freqBand        = [0.5 40];
unlockInfo.main.filterType      = 'butter';
unlockInfo.main.filterOrder     = 2;                    % Intended to be 4, filtfilt doubles filter order.
unlockInfo.main.doFilterData    = false;

%% Electrodes location
unlockInfo.main.elecLoc{1}  = 'PO7'; 
unlockInfo.main.elecLoc{2}  = 'O1'; 
unlockInfo.main.elecLoc{3}  = 'Oz'; 
unlockInfo.main.elecLoc{4}  = 'O2';
unlockInfo.main.elecLoc{5}  = 'PO8';
unlockInfo.main.elecLoc{6}  = 'Pz';
unlockInfo.main.elecLoc{7}  = 'Cz'; 
unlockInfo.main.elecLoc{8}  = 'AF8';

%% Epoch info
unlockInfo.epoch.trialLen       = '3 + iti?';               % trial length in seconds (fixation, delay, reward...time flashing lasts before decoding)
unlockInfo.epoch.changedTrialLen= false;                    % flag indicating epochs length has been changed due to problems in trials size (diff. number of samples, some lag in decoderTrial trigger)
unlockInfo.epoch.endTrialFlag   = unlockInfo.main.endTrialFlag;  % flag to signal end of 3 sec trial epoch data
unlockInfo.epoch.doEpochs       = false;                    % logical. True to separate epochos/trials
unlockInfo.epoch.doTrimEpochs   = true;                    % cuts epochs to get data from appropriate epochs only. Reducing length but assuring frequency of stim is correct
unlockInfo.epoch.fromEnd        = true;                     % extract epochs from the end to the start. If false start from first sample.
unlockInfo.epoch.startGap       = 0.1;                      % in seconds. extra time after dcd trigger is included. To assure data is from same trial (when size of trial changes during recording)
unlockInfo.epoch.endGap         = 0.1;                      % in seconds. time removed before dcd trigger is stamped. To assure data is from same trial and no spill over to next trial (when size of trial changes during recording)

%% Behavioral info
unlockInfo.behav.restLen = 0;
unlockInfo.behav.stimLen = 3;
unlockInfo.behav.delayDur = '';

%% Decoder info
unlockInfo.decoder.targets  = [12,13,14,15];% Possible targets. 
unlockInfo.decoder.nTgts    = length(unlockInfo.decoder.targets);  % total number of targets
unlockInfo.decoder.dcdCh    = 'Oz';
unlockInfo.decoder.dcdType  = 'hsd';        % decoder type. Harmonic sum decision 'HSD'

% Get stim frequencies based on file name. Unlock should give this info
if unlockInfo.main.triggeredData
    % To find stimFreq when only one is presented per session
    unlockInfo.decoder.stimFreq = getStimFreqFromName(unlockInfo);
    unlockInfo.epoch.doTrimEpochs   = false;                    % cuts epochs to get data from appropriate epochs only. Reducing length but assuring frequency of stim is correct
else
    % To find stimFreq for two frequencies alternating in a session
    indxFreq = strfind(unlockInfo.main.parentFile,'collector');     % Finding values of stim freqs.
    kk = 0;
    for iFreq = 1:unlockInfo.decoder.nTgts
        freqPos = strfind(unlockInfo.main.parentFile(indxFreq+8:end),num2str(unlockInfo.decoder.targets(iFreq)));
        if  ~isempty(freqPos)
            kk = kk +1;
            unlockInfo.decoder.stimFreq(iFreq) = unlockInfo.decoder.targets(iFreq);
        end
    end
end

%% Plot Params
unlockInfo.plot.lineWidth   = 5;         	% line width
unlockInfo.plot.colors(1,:) = [0 0 1];      % color of line plot       

unlockInfo.plot.chStart     = 1;          	% 2-4: O1,Oz,O2
unlockInfo.plot.chEnd       = 6;            % Channels plotted
unlockInfo.plot.freq1       = 8;            % lower bound frequency
unlockInfo.plot.freq2       = 19;           % higher bound frequency
unlockInfo.plot.windSz      = 5;            % Size of plotted window
unlockInfo.plot.movWind     = 0.5;          % Size of window moves
unlockInfo.plot.harmoNum    = 1;            % harmonics to plot. Zero for basic frequency. 1 for first harmonic.
unlockInfo.plot.typePlot    = 'spectAll';    %type of plot
% 'spectAll'        % spectrum for all channels. 
% 'specAll'         % spectrogram all channels. 2-4 are O1, Oz, O2
% 'specWindow'      % Plots spectrograms with a window size
% 'eachAllSpec'
% 'onlyOs'          % only occipital channles
% 'timeWindow'      % time signal for several channels, windowed
% 'eachAllTime'     % whole time trace for each channel
% 'specDcdTgt'      % spectrogram, windowed, with decoded target

% if strcmp(unlockInfo.plot.typePlot,'spectAll')
%     unlockInfo.plot.harmoNum = -1;
% end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function stimFreq = getStimFreqFromName(unlockInfo)

possibleVals = {'11hz','12hz','13hz','14hz','15hz','16hz','17hz','18hz'};
for iVals = 1:length(possibleVals)
    indxVal = strfind(unlockInfo.main.parentFile,possibleVals{iVals});
    if ~isempty(indxVal)
        indxPos = indxVal; 
    end
end
stimFreq = str2double(unlockInfo.main.parentFile(indxPos:indxPos+1));
warning('Getting stimFreq by means of the file''s name!!')
