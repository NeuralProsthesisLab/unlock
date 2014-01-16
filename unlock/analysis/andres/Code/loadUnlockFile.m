function [unlockData,unlockInfo] = loadUnlockFile(unlockInfo)
% function [unlockData,unlockInfo] = loadUnlockFile(unlockInfo.main.)
% 
% Loads the recorded data and creates structures with useful information
% for further analysis. Data from recorded EEG channels is in milliVolts. 
%
%
%
% Andres. V1. 17 Dec 2013

nCols = unlockInfo.main.nCols;                             % Number of EEG leads and extra channels (EMG, EOG, triggers)
nChs = unlockInfo.main.nChs;                                   % number of channels

%% Loading file
fileID  = fopen(unlockInfo.main.parentFile);
if fileID ~= -1                         % load only if the file exists
    rawCol  = textscan(fileID,'%d32');              % all data in one stream
    nIter   = length(rawCol{1})/nCols;              % total number of sample iterations (times data from all channels is collected)
    rawData = nan(nIter,nCols);                     % initializing data vble
    posData = nan(nIter,2);                         % sample number of data sampling iteration
    % Build the matrix with data per sampling clock time
    for iIter = 1:nIter
        iStart = (iIter-1)*nCols + 1;               % start of trial
        iEnd = (iIter)*nCols;                       % end of
        rawData(iIter,:) = rawCol{1}(iStart:iEnd);  % place data in bulks of nCols
        posData(iIter,:) = [iStart,iEnd];
    end
    % Verifying loading gave correct values using textread
    rawDataRead = textread(unlockInfo.main.parentFile);      %#ok<*REMFF1>
    if ~isequal(rawData,rawDataRead)
        warning('Loaded file does not match the one loaded with textread!!')
    end
else                                    % textread will not be supported in the future
    warning('File %s does not exist in the specified folder!!\n',unlockInfo.main.fileName)
end
fclose(fileID);                          % closing file

szData = size(rawData);
% Checking orientation of data. Always columns will be channels, rows
% samples
if szData(1) < szData(2)
    rawData = rawData';
end
  
%% Data processing done in the bioamplifier, sampling frequency and resolution
% This should originally be saved in an info structure included in the loaded files
switch unlockInfo.main.systemID
    % Enobio
    case 'enobio'
        Fs = 512;
        chSensit    = '';                       % channel sensitivity is '' microvolts, passing from micro to millivolts 
        filtHigh    = '';                       % high pass bound for filter
        filtLow     = '';                       % low pass bound for filter 
        resolutFactor = ''; % resolution factor to multiply raw data to get it in ?V 

	% gTec's Mobilab
    case 'mobilab'
        Fs = 256;                               % Sampling frequency
        chSensit    = 500;                      % channel sensitivity is 500 microvolts
        filtHigh    = 0.5;                      % high pass bound for filter
        filtLow     = 100;                      % low pass bound for filter
        %data = (int16 value)*(2*5/(2^16*4))*(Channel Sensitivity in µV) [µV]  
        resolutFactor = (2*5/(2^16*4))*(chSensit); % resolution factor to multiply raw data to get in µV.
    otherwise
        warning('The specified system,%s, is not supported...yet!',systemID)
end

%% Getting events, end of trial flags and decoded target (from the harmonic sum decision -HSD-)
unlockData.endTrl   = abs(rawData(:,11));       % end of trial flags (-1 by default)
unlockData.dcdTgt   = rawData(:,12);            % decoded target, given by the HSD

%% Taken only the channels with real info
unlockData.data     = rawData(:,1:nChs)*resolutFactor*1000;     % Multiplying by 1000 to get data from µV to mV.

%% Getting file info
unlockInfo.main.szData      = szData;           % data size
unlockInfo.main.nTrials     = sum(unlockData.endTrl);       % total number of trials
unlockInfo.main.nChs        = nChs;             % number of channels
unlockInfo.main.len         = unlockInfo.main.szData(1);    % length in samples
unlockInfo.main.Fs          = Fs;               % sampling frequency
unlockInfo.main.chSensit    = chSensit;         % channel sensitivity is 500 microvolts, passing from micro to millivolts
unlockInfo.main.filtHigh    = filtHigh;         % high pass bound for filter [Hz]
unlockInfo.main.filtLow     = filtLow;          % low pass bound for filter [Hz]
unlockInfo.main.resolutFactor = resolutFactor;  % resolution factor to multiply raw data to get it in ?V
