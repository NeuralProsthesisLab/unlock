function [specData,SpecInfo] = getUnlockSpecgram(eegData,SpecInfo)
%
% Calculates the spectrogram using chronux's multitaper functions 
%
% INPUT
% eegData:      matrix. This is the EEG raw data. Has to be in the form [samples x channels]
%
% OUTPUT
% 
% Andres. v1.0
% Created 15 Dec 2013
% Last modified 24 Dec 2013

nChs = SpecInfo.nChs;

%% Calculating the spectrogram

if isfield(SpecInfo,'nEpochs') && SpecInfo.doEpochs
    % For epochs,
    % if isfield(unlockInfo.epoch,'nOdds')
    % eegData(:,:,:,1);
    % eegData(:,:,:,2);
    % Getting the size of spectrogram
    [firstSpec,~,~] = mtspecgramc(squeeze(eegData(:,:,1,1)),SpecInfo.movingWin,SpecInfo.params);
    % Initial vble
    eegDataSpec = nan(size(firstSpec,1),size(firstSpec,2),nChs,2);
    % Getting the spectrogram
    tic
    for iTrial = 1:SpecInfo.nOdd       % number of epochs
        fprintf('Processing epoch %i\n',iTrial);
        [eegDataSpec(:,:,:,iTrial,1),~,~] = mtspecgramc(squeeze(eegData(:,:,iTrial,1)),SpecInfo.movingWin,SpecInfo.params);
        [eegDataSpec(:,:,:,iTrial,2),tspec,fspec] = mtspecgramc(squeeze(eegData(:,:,iTrial,2)),SpecInfo.movingWin,SpecInfo.params);
    end
    toc
    % Super structure
    specData.data = eegDataSpec;
    specData.tspec = tspec;
    specData.fspec = fspec;
else
    % for all the data
    [specData.data,specData.tspec,specData.fspec] = mtspecgramc(eegData,SpecInfo.movingWin,SpecInfo.params);
end

%% Spec analysis transformation factors
SpecInfo.tspec      = specData.tspec;
SpecInfo.fspec      = specData.fspec;
SpecInfo.specData   = {'T','Freq.','chs','epoch','stimFreq'};
SpecInfo.size       = size(specData.data);
SpecInfo.FreqRes    = specData.fspec(3) - specData.fspec(2);
SpecInfo.hz2spec    = length(specData.fspec)/SpecInfo.freqResolut;
SpecInfo.sec2spec   = length(specData.tspec)/(length(eegData)/SpecInfo.freqResolut);

% %% Saving matrix and info structure
% if exist(fullfile(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms'))
% else
%     mkdir(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms')
% end
% saveFile = fullfile(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms',sprintf('specgram_%s_AllChs_TW%iK%iwind%0.1ewinstep%0.1e.mat',session,SpecInfo.params.tapers(1),SpecInfo.params.tapers(2),SpecInfo.movingWin(1),SpecInfo.movingWin(2)));
% SpecInfo.saveFile = saveFile;
% save(saveFile,'dataSpec','SpecInfo','-v7.3');
%  
