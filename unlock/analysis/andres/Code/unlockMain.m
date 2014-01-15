function onlinePerf = unlockMain(fileName)
% function onlinePerf = unlockMain(fileName)
%
% Main function for analysis of unlock recorded data
%
%
%
%
% Andres. V1. 18 Dec 2013
% Last modified 07 Jan 2014

%% Set folders and paths
unlockInfo.main.dirs = initUnlockDirs;

%% FileName
%if nargin == 0                              % Custom fileName
    %unlockInfo.main.parentFile  = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\raw\20131217-mobilab\collector_mobilab_12_13_3minutes.txt';
    %unlockInfo.main.parentFile  = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\raw\20131217-mobilab\collector_mobilab_14_15_3minutes.txt';
    %fileName  = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\raw\20140106-mobilab\mobilab-single-ssvep-diag-15hz_1389043288.txt';
    unlockInfo.main.systemID    = 'mobilab';       % Data recording system
% else                                        % Fixed fileName (how it should be always)
%     session     = '20131217-mobilab';
%     rawName     = 'collector_mobilab_12_13_3minutes';
%     unlockInfo.main.fileName    = sprintf('%s.txt',fullfile(unlockInfo.main.dirs.DataIn,session,rawName));
% end
unlockInfo.main.parentFile = fileName;

%% Set Unlock Params
unlockInfo = setUnlockParams(unlockInfo);

%% Load file
[unlockData,unlockInfo] = loadUnlockFile(unlockInfo); fprintf('Just loaded the file %s!!!\n',fileName)

%% Filter data
[unlockFiltData,unlockInfo] = filtData(unlockData,unlockInfo);
unlockData.data = unlockFiltData; disp('Just filtered the data!!!')

%% Epoch data using the endTrialFlag
[unlockEpochs,unlockInfo,dcdTgt,epochDcdTgt] = getUnlockEpochs(unlockData,unlockInfo);

%% Getting decoder values
onlinePerf = onlinePerform(dcdTgt,unlockInfo);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Epoch data analysis
if unlockInfo.epoch.doEpochs
    %% Epoch data using the endTrialFlag
    [unlockEpochs,unlockInfo,dcdTgt,epochDcdTgt] = getUnlockEpochs(unlockData,unlockInfo);
    
    %% Online decoder performance
    onlinePerf = onlinePerform(dcdTgt,unlockInfo);
    
    %% Plotting decodeTrial triggers
    if unlockInfo.plot.doPlot
        plotDcdTrigSamp(dcdTgt,epochDcdTgt,unlockInfo)
    end
    
    %% Epoch spectrum
    if unlockInfo.epoch.doSpectrum
        SpectInfo.Fs        = unlockInfo.main.Fs;
        SpectInfo.nChs      = unlockInfo.main.nChs;
        SpectInfo.freqBand  = unlockInfo.main.freqBand;
        SpectInfo.nEpochs   = unlockInfo.epoch.nEpochs;
        SpectInfo.doEpochs  = unlockInfo.epoch.doEpochs;
        SpectInfo.nOdd      = unlockInfo.epoch.nOdd;
        %SpecParams          = SpectInfo;
        [SpectInfo]         = setDefaultSpecParams(SpectInfo);
        %SpectInfo            = SpecParams;
        %SpectInfo.params    = SpecInfo.params;
        eegData             = unlockEpochs;
        [spectData,SpectInfo]   = getUnlockSpectrum(eegData,SpectInfo);
        unlockInfo.epoch.spect  = SpectInfo;
        
        %% Extracting epoch's spectrum features
        featData = spectData;
        [dataFeatures,unlockInfo] = extractFeat(featData,unlockInfo);
        
        %% Decode based on Oz
        dcdData = spectData;
        [dcdVals,unlockInfo] = decodeEpochs(dcdData,unlockInfo);
    end
    
    %% Epoch's Spectrograms
    if unlockInfo.epoch.doSpecgram
        eegData = unlockEpochs;
        SpecInfo.nEpochs = unlockInfo.epoch.nEpochs;
        SpecInfo.doEpochs = unlockInfo.epoch.doEpochs;
        SpecInfo.nOdd = unlockInfo.epoch.nOdd;
        [specData,SpecInfo] = getUnlockSpecgram(eegData,SpecInfo);
        unlockInfo.epoch.spec = SpecInfo;
    end
end

%% Raw time Spectrum
if unlockInfo.main.doSpectrum
    SpectInfo.Fs         = unlockInfo.main.Fs;
    SpectInfo.nChs       = unlockInfo.main.nChs;
    SpectInfo.freqBand   = unlockInfo.main.freqBand;
    eegData             = unlockData.data;
    SpectInfo            = setDefaultSpecParams(SpectInfo);       % Need a setDefaultParams function
    % Get spectrum
    [spectData,SpectInfo] = getUnlockSpectrum(eegData,SpectInfo);
    unlockInfo.analysis.spectInfo = SpectInfo; disp('Just got the spectrum!!!')
    spectData.tspec = [];
    
    %% Plot spectrum
    if unlockInfo.plot.doPlot
        unlockInfo.plot.typePlot = 'spectAll';
        hFig = plotUnlockTimeSpec(unlockData,spectData,SpectInfo,unlockInfo);
        
    end
end

%% Raw time Spectrogram
if unlockInfo.main.doSpecgram
    % Set default spectrogram params
    SpecInfo.Fs         = unlockInfo.main.Fs;
    SpecInfo.nChs       = unlockInfo.main.nChs;
    SpecInfo.freqBand   = unlockInfo.main.freqBand;
    eegData             = unlockData.data;
    %SpecParams          = SpecInfo;
    SpecInfo            = setDefaultSpecParams(SpecInfo);       % Need a setDefaultParams function
    %SpecInfo            = SpecParams;
    % Get spectrogram
    [specData,SpecInfo] = getUnlockSpecgram(eegData,SpecInfo);
    unlockInfo.analysis.specInfo = SpecInfo; disp('Just got the spectrogram!!!')
    
    %% Plot spectrogram
    if unlockInfo.plot.doPlot
        unlockInfo.plot.typePlot = 'specAll';
        hFig = plotUnlockTimeSpec(unlockData,specData,SpecInfo,unlockInfo);
    end
end

%% Save spectrum/spectrogram figure
if unlockInfo.main.saveFig
    figName = unlockInfo.main.parentFile(strfind(lower(unlockInfo.main.parentFile),'hz')-2:end-4);    
    % Window size text
    if strcmp(unlockInfo.plot.typePlot,'spectAll')
        lenWindow = '';
    elseif isfield(unlockInfo.analysis,'specInfo')
        % size of window for spectrogram
        lenWindow = ['-',num2str(unlockInfo.analysis.specInfo.movingWin(1)),'sec'];
    end
    
    % Harmonics text
    if unlockInfo.plot.harmoNum == 0;            % harmonics to plot. Zero for basic frequency. 1 for first harmonic.
        harmoNum = '-0Harm';
    elseif unlockInfo.plot.harmoNum == 1
        harmoNum = '-1stHarm';
    else
        warning('No harmonics!!')
    end
    
    % Save
    saveFilename = sprintf('%s%s%s-%s.png',fullfile(unlockInfo.main.dirs.DataOut,unlockInfo.plot.typePlot),lenWindow,harmoNum,figName);
    saveas(hFig,saveFilename)
    disp('Just saved the figure!!!')
end


