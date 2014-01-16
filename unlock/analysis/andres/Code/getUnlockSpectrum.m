function [spectData,SpectInfo] = getUnlockSpectrum(eegData,SpectInfo)
%
% Calculates the spectrogram using chronux's multitaper functions 
%
% INPUT
% eegData:      matrix. This is the EEG raw data. Has to be in the form [samples x channels]
%
% OUTPUT
% 
%

nChs = SpectInfo.nChs;

%% Calculating the spectrogram

if isfield(SpectInfo,'nEpochs') && SpectInfo.doEpochs
    % For epochs,
    % if isfield(unlockInfo.epoch,'nOdds')
    % eegData(:,:,:,1);
    % eegData(:,:,:,2);
    % Getting the size of spectrogram
    [firstSpec,~] = mtspectrumc(squeeze(eegData(:,:,1,1)),SpectInfo.params);
    % Initial vble
    eegDataSpec = nan(size(firstSpec,1),nChs,2);
    % Getting the spectrogram
    tic
    for iTrial = 1:SpectInfo.nOdd       % number of epochs
        fprintf('Processing epoch %i\n',iTrial);
        [eegDataSpec(:,:,iTrial,1),~] = mtspectrumc(squeeze(eegData(:,:,iTrial,1)),SpectInfo.params);
        [eegDataSpec(:,:,iTrial,2),fspec] = mtspectrumc(squeeze(eegData(:,:,iTrial,2)),SpectInfo.params);
    end
    toc
    % Super structure
    spectData.data = eegDataSpec;
    spectData.fspec = fspec;
else
    % for all the data
    [spectData.data,spectData.fspec] = mtspectrumc(eegData,SpectInfo.params);
end

%% Spec analysis transformation factors
SpectInfo.fspec      = spectData.fspec;
SpectInfo.specData   = {'Freq.','chs','epoch','stimFreq'};
SpectInfo.size       = size(spectData.data);
SpectInfo.FreqRes    = spectData.fspec(3) - spectData.fspec(2);
SpectInfo.hz2spec    = length(spectData.fspec)/(SpectInfo.freqResolut);
warning('CHECK IF freqREsolut IS BETTER THAN Fs/2 TO GET PROPER FREQ. limits when plotting!')

% %% Saving matrix and info structure
% if exist(fullfile(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms'))
% else
%     mkdir(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms')
% end
% saveFile = fullfile(BCIinfo.dirs.saveFilename(1:end-10),'Spectrograms',sprintf('specgram_%s_AllChs_TW%iK%iwind%0.1ewinstep%0.1e.mat',session,SpecInfo.params.tapers(1),SpecInfo.params.tapers(2),SpecInfo.movingWin(1),SpecInfo.movingWin(2)));
% SpecInfo.saveFile = saveFile;
% save(saveFile,'dataSpec','SpecInfo','-v7.3');
%  
