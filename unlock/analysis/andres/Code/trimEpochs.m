function [trimmedEpochs,trimDcdTgt,epochDcdTgt,unlockInfo] = trimEpochs(unlockEpochs,unlockInfo,epochDcdTgt,dcdTgt) 
% function [trimmedEpochs,trimDcdTgt,epochDcdTgt,unlockInfo] = trimEpochs(unlockEpochs,unlockInfo,epochDcdTgt,dcdTgt)
%
% Trims the epochs to include only data from that trial. Useful when not
% sure boundaries of epoch are from same trial or from previous or next
% one. 
%
% boundaries from both sides are removed based on location of the decoded
% trial end trigger and epoch extraction method (fromEnd or not) and location
% 
%
%
% Andres. v1.1      02 Jan 2014
% Last modified:    02 Jan 2014

%% Getting trimming boundaries
if unlockInfo.main.triggeredData
    trigPos = unique(dcdTgt.samp);
    trimStart = round(unlockInfo.epoch.startGap*unlockInfo.main.Fs);
    trimEnd = trigPos - round(unlockInfo.epoch.endGap*unlockInfo.main.Fs);
    trimDcdTgt = dcdTgt;
else
    if unlockInfo.epoch.fromEnd
        % If epochs extracted from decodedTrial trigger (at end of trial) and
        % moving backwards (trigger is at end of trial but last samples might be from next epoch)
        trigPos = unique(dcdTgt.samp);
        trimStart = round(unlockInfo.epoch.startGap*unlockInfo.main.Fs);
        trimEnd = trigPos(2) - round(unlockInfo.epoch.endGap*unlockInfo.main.Fs);
        trimDcdTgt = dcdTgt;
    else
        % If epochs extracted from first sample (end of trial spills over next trial, first samples might be from previous epoch)
        trimStart = max(dcdTgt.samp) + round(unlockInfo.epoch.startGap*unlockInfo.main.Fs);
        trimEnd = unlockInfo.epoch.trialSampLen;
        
        % Moving decoded-trial-trigger values to previous epoch
        trimDcdTgt = dcdTgt;
        trimDcdTgt.val = circshift(dcdTgt.val,-ones(1,unlockInfo.epoch.nEpochs));       % shifting to previous epoch the trigger values
        
        % Last decoder trigger
        trigPos = unique(dcdTgt.leftOvers.dcdTgt);                                      % last trigger from leftOver data
        if length(trigPos) >= 2
            lastTrig = trigPos(2);
        else
            lastTrig = trigPos(1);
        end
        trimDcdTgt.val(end) = lastTrig;
    end
end

%% Trim epochs
trimmedEpochs = unlockEpochs(trimStart:trimEnd,:,:,:);
tmpDcdTgt = epochDcdTgt(trimStart:trimEnd,:);
tmpDcdTgt(end,:) = epochDcdTgt(end,:);
epochDcdTgt = tmpDcdTgt;

%% Changing values in info structure
unlockInfo.epoch.trialSampLen = trimEnd - trimStart + 1;
unlockInfo.epoch.changedTrialLen = true;

