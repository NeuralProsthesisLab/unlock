function [unlockEpochs,unlockInfo,dcdTgt,epochDcdTgt] = getUnlockEpochs(unlockData,unlockInfo)
%
% Gets epochs for unlock based on end of trial flags located in
% unlockData.endTrial vector.
%
%
%
%
%
% Andres v1. 18 Dec 2013 

% Data
eegData     = unlockData.data;
eegTime     = 0:1/unlockInfo.main.Fs:unlockInfo.main.len;
eegEndTri   = unlockData.endTrl;
eegDcdTgt   = unlockData.dcdTgt;
% fspec       = specData.fspec;
% tspec       = specData.tspec;

% Params
Fs          = unlockInfo.main.Fs;
nChs        = unlockInfo.main.nChs;
nTrials     = unlockInfo.main.nTrials;
expTgts     = unlockInfo.decoder.stimFreq;
stimLen     = unlockInfo.behav.stimLen;
restLen     = unlockInfo.behav.restLen;


trialLen    = (stimLen + restLen)*Fs;               % trial length in samples
unlockInfo.epoch.trialSampLen = trialLen;           % do this here since later is it changed

%% Extracting all epochs
% For triggered epochs
if unlockInfo.main.triggeredData
    epochIndx   = (find(eegEndTri));
    nEpochs     = numel(epochIndx);
    eegAllEpochs = nan(trialLen,nChs,nEpochs);
    for iIndx = 1:nEpochs    % moving from the end to the beginning (MUST DOUBLE CHECK SAMPLES ALIGNED)
        eegAllEpochs(:,:,iIndx)     = eegData(epochIndx(iIndx) - trialLen + 1:epochIndx(iIndx),:);      % epoch's samples
        epochDcdTgt(:,iIndx)        = eegDcdTgt(epochIndx(iIndx) - trialLen + 1:epochIndx(iIndx));  	% window of decoded targets
        warning('MUST DOUBLE CHECK SAMPLES ALIGNED')
    end
    % Extra data left, usefull if problems aligning data
    if epochIndx(iIndx) < unlockInfo.main.szData(1)
        leftOvers.eegData   = eegData(epochIndx(iIndx):end,:);
        leftOvers.dcdTgt    = eegDcdTgt(epochIndx(iIndx):end);
    else
        leftOvers.eegData = [];
        leftOvers.dcdTgt = [];
    end
% When not all trials have an end Trigger
else
    if unlockInfo.epoch.fromEnd
        % Start getting epochs from last trigger
        % Number epochs
        indx        = find(eegEndTri);                  % samples where trial labeled as ended
        iEpoch      = 0;
        nEpochs     = length(max(indx):-trialLen:1) - 1;
        eegAllEpochs = nan(trialLen,nChs,nEpochs);
        
        for iIndx = max(indx):-trialLen:1               % moving from the end to the beginning (MUST DOUBLE CHECK SAMPLES ALIGNED)
            iEpoch = iEpoch +1;
            if iEpoch <= nEpochs
                %loco(iEpoch,:) = [iIndx-trialLen-1,iIndx-1];
                eegAllEpochs(:,:,iEpoch)    = eegData(iIndx-trialLen+1:iIndx,:);        % epoch's samples
                epochDcdTgt(:,iEpoch)       = eegDcdTgt(iIndx-trialLen+1:iIndx);      % window of decoded targets
                warning('MUST DOUBLE CHECK SAMPLES ALIGNED')
                warning('epochDcdTgt MUST BE TRimmed as Well')
                
            end
        end
        % Extra data left, usefull if problems aligning data
        leftOvers.eegData = eegData(1:iIndx,:);
        leftOvers.dcdTgt = eegDcdTgt(1:iIndx);
    else
        % Start extracting epochs from first sample
        nEpochs = length(1:trialLen:unlockInfo.main.szData(1)-trialLen);
        eegAllEpochs = nan(trialLen,nChs,nEpochs);
        iEpoch      = 0;
        for iIndx = 1:trialLen:unlockInfo.main.szData(1)-trialLen    % moving from the end to the beginning (MUST DOUBLE CHECK SAMPLES ALIGNED)
            iEpoch = iEpoch + 1;
            eegAllEpochs(:,:,iEpoch)    = eegData(iIndx:iIndx+trialLen - 1,:);        % epoch's samples
            epochDcdTgt(:,iEpoch)       = eegDcdTgt(iIndx:iIndx+trialLen - 1);      % window of decoded targets
            warning('MUST DOUBLE CHECK SAMPLES ALIGNED')
        end
        % Extra data left, usefull if problems aligning data
        if iIndx+trialLen < unlockInfo.main.szData(1)
            leftOvers.eegData = eegData(iIndx+trialLen:end,:);
            leftOvers.dcdTgt = eegDcdTgt(iIndx+trialLen:end,:);
        else
            leftOvers.eegData = [];
            leftOvers.dcdTgt = [];
        end
    end
end

% Only for even epochs when 2 stimuli presented
if ~numel(unlockInfo.decoder.stimFreq) == 1
    if mod(nEpochs,2)
        nEpochs = nEpochs - 1;       % Need even trials, the same for both stimulation frequencies
    end
end
unlockInfo.epoch.nEpochs = nEpochs;

%% Get decoded target per epoch
dcdTgt.val      = zeros(1,nEpochs);             % decoded target
dcdTgt.samp     = zeros(1,nEpochs);             % sample in which decoded target values was saved
[row,col,val]   = find(epochDcdTgt);            % finding indexes for decoded target for each epoch. Sample where dcdTgt is located in the epoch
dcdTgt.val(col) = val;
dcdTgt.samp(col)= row;
dcdTgt.leftOvers = leftOvers;                       % extra data due to abrupt end of trial or trial size issues

%% Get unlockEpochs
if ~numel(unlockInfo.decoder.stimFreq) == 1    
    %% Only for even epochs when 2 stimuli presented
    % Get both frequency epochs
    oddEp = 1:2:nEpochs;                            % odd epochs
    eveEp = 2:2:nEpochs;                            % even epochs
    unlockEpochs = nan(trialLen,nChs,nEpochs/2,2);
    unlockEpochs(:,:,:,1) = eegAllEpochs(:,:,oddEp);% data samples for odd epochs
    unlockEpochs(:,:,:,2) = eegAllEpochs(:,:,eveEp);% data samples for even epochs
else
    unlockEpochs(:,:,:,1) = eegAllEpochs;
end
     
%% Remove edges from epochs to have some certainty decoding data is from same trial
if unlockInfo.epoch.doTrimEpochs
    [trimmedEpochs,trimDcdTgt,epochDcdTgt,unlockInfo] = trimEpochs(unlockEpochs,unlockInfo,epochDcdTgt,dcdTgt);
end

if ~numel(unlockInfo.decoder.stimFreq) == 1
    % Get decoded target after trimming epochs
    dcdTgt.oddEpoch     = dcdTgt.val(oddEp);        % decoded target for odd epochs
    dcdTgt.eveEpoch     = dcdTgt.val(eveEp);        % decoded target for even epochs
    % Add info to unlockInfo structure
    unlockInfo.epoch.nOdd = length(oddEp);
    unlockInfo.epoch.nEve = length(eveEp);
else
end

% % Check order of epochs and stimuli
% unlockInfo.decoder.stimFreq(1);                      % matches the last extracted epoch
% % create vector nVals = nTrials -> expected target!
% 
% unlockInfo.epoch.nTrials = size(eegAllEpochs,3);    %available trials (not total since after last decoded one could be more)
% % Average epochs per stim freq.
% 
% 
% % Good Epochs
% indx = find(eegEndTri);
% eegDcdEpochs = eegData(indx-stimLen*Fs:indx,:);
% 
% % Plot Epochs