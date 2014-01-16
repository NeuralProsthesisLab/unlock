function [dataFeatures,unlockInfo] = extractFeat(featData,unlockInfo)
%
%
%
%
%
%
%

% Vbles
stimFreq = unlockInfo.decoder.stimFreq;
dcdCh = unlockInfo.decoder.dcdCh;
dcdType = unlockInfo.decoder.dcdType;
tgtStim = unlockInfo.decoder.targets;
nTgt = unlockInfo.decoder.nTgts;

% Find electrode position
dcdChIndx = find(strcmp(unlockInfo.main.elecLoc,dcdCh)); % index in data file of channel chosen for decoding

% Removing unimportant frequencies
rawData = featData.data;
freqVals = featData.fspec;

% Find freq. vals in range of freq. of interest
% Finding freq. position 
freqPos = nan(2,nTgt);
for iTgt = 1:nTgt 
    [~,freqPos(1,iTgt),~] = intersect(freqVals,tgtStim(iTgt));       % main frequency.
    [~,freqPos(2,iTgt),~] = intersect(freqVals,2*tgtStim(iTgt));     % first harmonic
end


freqVals(freqPos)

% Find boundaries for plotting


startIndx = 45;
endIndx = 60;
% Plotting Odd epochs spectrum
oddData = squeeze(rawData(:,dcdChIndx,:,1));
for iTrial = 1:unlockInfo.epoch.nOdd
    plot(freqVals(startIndx:endIndx),oddData(startIndx:endIndx,iTrial))
    title(sprintf('Odd freq. %i, trial %i',stimFreq(1),iTrial))
    axis tight
    pause
end

% Plotting even epochs spectrum
eveData = squeeze(rawData(:,dcdChIndx,:,2));
stimFreq(2)


dataFeatures = featData;