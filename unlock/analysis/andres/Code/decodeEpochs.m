function [dcdVals,unlockInfo] = decodeEpochs(dcdData,unlockInfo)
%
%
%
%
%
%
%
%

% Getting vbles
data = dcdData.data;
% timeVals = dcdData.tspec;
if unlockInfo.main.triggeredData
    
elseif isfield(unlockInfo.epoch,'spec') || isfield(unlockInfo.epoch,'spec')
    freqVals = dcdData.fspec;
    % Plot trials
    for iTrial = 1:30, plot(freqVals,data(:,3,iTrial,1)), title(num2str(iTrial)),pause,end
end

stimFreq = unlockInfo.decoder.stimFreq;
dcdCh = unlockInfo.decoder.dcdCh;
dcdType = unlockInfo.decoder.dcdType;
tgtStim = unlockInfo.decoder.targets;
nTgt = unlockInfo.decoder.nTgts;

% switch lower(dcdType)
%     case 'hsd'
%% For HSD

% Finding freq. position 
freqPos = nan(numel(stimFreq),nTgt);
for iTgt = 1:nTgt 
    [~,freqPos(1,iTgt),~] = intersect(freqVals,tgtStim(iTgt));       % main frequency.
    [~,freqPos(2,iTgt),~] = intersect(freqVals,2*tgtStim(iTgt));     % first harmonic
end

freqVals(freqPos)
% Find electrode position
dcdChIndx = find(strcmp(unlockInfo.main.elecLoc,dcdCh)); % index in data file of channel chosen for decoding
%end    %end for switch option