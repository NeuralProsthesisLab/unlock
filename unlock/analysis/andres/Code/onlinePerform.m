function onlinePerf = onlinePerform(dcdTgt,unlockInfo)
% function onlinePerf = onlinePerform(dcdTgt,unlockInfo)
%
%
%
%
%
%
% Andres v.1
% Created 29 Jan 2013 
% Las modified 03 Jan 2014

if isempty(strcmp(unlockInfo.main.parentFile,'collector'))
    % For two stim frequencies
    stimFreq = find(unlockInfo.decoder.stimFreq);
    onlinePerf.overallf1 = sum(stimFreq(1) == dcdTgt.oddEpoch)/unlockInfo.epoch.nOdd;
    onlinePerf.overallf2 = sum(stimFreq(2) == dcdTgt.eveEpoch)/unlockInfo.epoch.nEve;
    onlinePerf.dcdOnlyf1 = (sum(stimFreq(1) == dcdTgt.oddEpoch(find(dcdTgt.oddEpoch))))/numel(dcdTgt.oddEpoch(find(dcdTgt.oddEpoch)));
    onlinePerf.dcdOnlyf2 = (sum(stimFreq(2) == dcdTgt.eveEpoch(find(dcdTgt.eveEpoch))))/numel(dcdTgt.eveEpoch(find(dcdTgt.eveEpoch)));

    %numel(find(dcdTgt.oddEpoch))
    %numel(find(dcdTgt.eveEpoch))
elseif unlockInfo.main.triggeredData
    % For one frequency per session
	stimFreq = find(unlockInfo.decoder.stimFreq == unlockInfo.decoder.targets);
    if isempty(stimFreq)
        stimFreq = -2;
    end
    onlinePerf.stimFreq = unlockInfo.decoder.stimFreq;
	onlinePerf.overallf = sum(stimFreq == dcdTgt.val)/unlockInfo.epoch.nEpochs;
    % Add info to unlockInfo structure
    onlinePerf.allEpochs = stimFreq*(stimFreq == dcdTgt.val);
    onlinePerf.dcdTgts = dcdTgt.val(dcdTgt.val ~= unlockInfo.main.endTrialFlag);
    onlinePerf.numDcdTgts = numel(onlinePerf.dcdTgts);
    onlinePerf.dcdOnlyf = sum(onlinePerf.dcdTgts == stimFreq)/onlinePerf.numDcdTgts;    
end

 
