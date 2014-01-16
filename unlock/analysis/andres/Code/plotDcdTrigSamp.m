function plotDcdTrigSamp(dcdTgt,epochDcdTgt,unlockInfo)
%
%
%
%
%
%

nEpochs = unlockInfo.epoch.nEpochs;
trialLen = unlockInfo.epoch.trialSampLen;
stimFreq = unlockInfo.decoder.stimFreq(find(unlockInfo.decoder.stimFreq));

% Name in the plot
if unlockInfo.main.triggeredData
    fromWhere = 'triggered';
else
    if unlockInfo.epoch.fromEnd
        fromWhere = 'FromEnd';
    else
        fromWhere = 'FromStart';
    end
end

% Histogram of dcdTrigger sample location
figure;
hist(dcdTgt.samp,trialLen)

% One stimulation frequency or two?
if unlockInfo.main.triggeredData    % One
    title(sprintf('Trigger loc. Trial length  %i. %s [%iHz]',trialLen,fromWhere,stimFreq(1)),'fontweight','bold')
else                                % Two
   	title(sprintf('Trigger loc. Trial length  %i. %s [%i-%iHz]',trialLen,fromWhere,stimFreq(1),stimFreq(2)),'fontweight','bold')
end
xlabel('Sample','FontWeight','bold')
ylabel('Count','FontWeight','bold')

% See each trial
figure;
for iEpoch = 1:nEpochs, plot(epochDcdTgt(:,iEpoch)), axis tight, title(num2str(iEpoch)), pause, end

