function [ptData,ptTime,ptInfo] = photodiodeMain(fileName)
% [ptData,ptTime,ptInfo] = photodiodeMain(fileName)
%
% Loads and parses data, creates photo diode and time vector0 Also a
% structure with info regarding smapling frequency, flickering stimulation
% freq. and times for sweep analysis.
%
% INPUT
% fileName:     string. Complete path and name, or only filename (if file 
%               in default DataIn folder) of the file to load. 
%
% OUTPUT
% ptData:           vector [1 x nSamples]. Vector with the photodiode data
% ptTime:           vector. [1 x nSamples]. Time vector, each sample is 
%                   represents time 
% ptInfo:           structure. Has infor regarding sampling freq., stimuli
%                   onset and offset.
%
%     nameFile:         parent file
%     HighStates:       integer. value representing a high state (when 
%                       stimulus checkboard was white). By default is 8
%     LowStates:        integer. value representing a low state (when 
%                       stimulus checkboard is black). By default is 0
%     sampFreq:         Sampling frequency. For USBamps is 256 Hz. For NEC 
%                       Enovio is 512 Hz
%     StimFreq:         vector. Common stimulation frequency used in the 
%                       checkeboard. By default for sweep is [12 13 14 15 16]
%     StimTimeSec:      integer. Duration of flickering in seconds. By 
%                       default 3
%     StimRestTimeSec:  integer period between flickering in seconds. By 
%                       default 3
%     SweepTimes:       matrix. [nDifferentFrequencies x TimeIn'ptTime'Vector].
%                       Start and End times when StimFreq was used. Each 
%                       row corresponds to each 'StimFreq'.    
%
% Andres. v1. 
% Last modified 11 Dec 2013

% Set directories and paths
dirs = initUnlockDirs;

% For testing
fileName = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\raw\20131211-photodiode\DiodeData_15.mat';

%Check if fileName is a path or a simple file name
if isempty(strfind(fileName,'\'))       % only filename
    if exist(fullfile(dirs.DataIn,fileName),'file')
        diodeData = load(fullfile(dirs.DataIn,fileName));
    else
        warning('File %s does not exist in the specified path',fileName);  %#ok<*WNTAG,*WNTAG>
    end
    
else     % complete path
    if exist(fullfile(fileName),'file')
        diodeData = load(fullfile(fileName));
    else
        warning('File %s does not exist in the %s folder',fileName,dirs.DataIn) %#ok<*WNTAG>
    end
end

% Checking rows are for channels and create 
[d1,d2] = size(diodeData.y);
if d1>d2
    diodeData.y = diodeData.y';
else
end

% Getting the stim frequencies
if strfind(fileName,'DiodeData_15')
    stimFreq = 15;
    titleStr = '15';
    %Get name of file to save it 
    strIndx = strfind(fileName,'DiodeData_15');
elseif strfind(fileName,'DiodeData_sweep')
    stimFreq = [12,13,14,15,16];
    titleStr = 'Sweep 12,13,14,15,16';
    strIndx = strfind(fileName,'DiodeData_sweep');
end
saveStr = fileName(strIndx(end)+10:end-4);

% Getting ptData only from EEG + PT
ptData = diodeData.y(34,:);
ptTime = diodeData.y(1,:);

% Sampling frequency
Fs = 1/(ptTime(3) - ptTime(2));

%% Extra analysis 

% Plot data
hFig = plot(ptTime, ptData); %#ok<NASGU>
title(fileName,'FontWeight','Bold')
xlabel('Sec','FontWeight','Bold'); ylabel('PhotoDiode State','FontWeight','Bold')

xRange = zeros(length(stimFreq),2);
SweepTimes = zeros(length(stimFreq),2);
% Get start of stimulation (flickering)
fprintf('Get ''start'' of stimulation for freq. %i\n',stimFreq(1))
[xRange(1),~] = ginput(1);

% Extract sections for each freq. (time boundaries)
if strfind(fileName,'DiodeData_sweep')
    % Get right most boundary 
    for iFreq = 2:length(stimFreq)+1
        fprintf('Get ''end'' of stimulation for freq. %i\n',stimFreq(iFreq-1))
        [xRange(iFreq),~] = ginput(1);
        SweepTimes(iFreq - 1,:) = [xRange(iFreq-1) xRange(iFreq)];
    end
else
    fprintf('Get ''end'' of stimulation/flickering for freq. %i\n',stimFreq(1))
    [xRange(1,2),~] = ginput(1);
    SweepTimes = xRange;
end

%% Filter the data 
% Filter params
smpRate     = Fs;
freqBand    = [1 Fs/2];
filterOrder = 2; 
filterType  = 'butter';
[filtParams]= setFilterParams(freqBand, filterType, filterOrder, smpRate);

% Filtering
dataFiltered = true;
ptData = filtfilt(filtParams.b,filtParams.a,ptData);

%% Running periodogram
[pxx,f] = periodogram(ptData,[],[],Fs);
%plot(f,10*log10(pxx))
plot(f,(pxx))
xlabel('Frequency'); ylabel('dB');
title(sprintf('Periodogram of photodiode %s',titleStr));

%% Info structure with info required for analysis
ptInfo = struct('nameFile',fileName,'HighStates',8,'LowStates',0,'sampFreq',Fs,'StimTimeSec',3,'StimRestTimeSec',3','StimFreq',stimFreq,'SweepTimes',SweepTimes); %#ok<NASGU>

% Saving files
if ~dataFiltered 
    saveFilename = ['PhotoDiodeDataAndTimes-',saveStr];
else
    saveFilename = sprintf('PhotoDiodeDataAndTimesFilt%0.1f-%i-%s',freqBand(1),freqBand(2),saveStr);
end    
% Matlab
save(sprintf('%s.mat',fullfile(dirs.DataOut,saveFilename)),'ptData','ptTime','ptInfo');
% Comma Separated Values (CSV)
photoDiode = [ptData;ptTime]';          %Putting files in column, one for time vector, another for photodiode (so Excel can open it)
csvwrite(sprintf('%s.csv',fullfile(dirs.DataOut,saveFilename)),photoDiode)

fprintf('\nSuccessfully saved all the files to %s as %s\n',dirs.DataOut,saveFilename)

end

function dirs = initUnlockDirs
% function dirs = initUnlockDirs
% 
% This fucntionb initializes all paths and sets default directories where 
% all data will be loaded and saved to. It can be set for different users.
% 
% OUTPUT: 
%
%   dirs:           Struct containing list of directory names needed to run 
%                   the data analysis code:
%     Code:         Dir w/ data analysis code.
%     DataIn:       Dir where 'raw' datafiles are to be read from.
%     DataOut:      Dir where analyzed datafiles and figures are to be written to 
%
% This code is pretty simmilar to the one used in the BlackRock to npl
% (init2npl.m) dataConversion code set by Scot Brincat.


%% Set appropriate directories for code, data input and output, based on system hostname.
[~,host] = system('hostname');
host     = deblank(host);

switch host
    case 'cns-ws15'
        dirs.Code       = 'C:\Users\salacho\Documents\Code\Unlock';                 % Dir w/ data analysis Code
        dirs.helpers    = 'C:\Users\salacho\Documents\Code\helpers';                % Dir w/ helpers analysis Code
        dirs.DataIn     = 'C:\Users\salacho\Documents\Analysis\unlock';             % Dir w/ datafiles. Mapping server using SFTP Net Drive
        dirs.DataOut    = 'C:\Users\salacho\Documents\Analysis\unlock';             % Local Dir to output analyzed datafiles and figures too
        dirs.BCIparams  = '';                                                       %Add path where all BCIparams are located
        dirs.PTB        = 'C:\Users\salacho\Documents\MATLAB\toolbox\Psychtoolbox'; % Add path to PsychToolbox
        dirs.chronux    = 'C:\Users\salacho\Documents\MATLAB\toolbox\chronux';      % Add path to chronux toolbox
    otherwise
        disp('No paths have been estalished')
end

% Set up path so code is accessible to Matlab
addpath(dirs.helpers);              % Add dir w/ my helpers
addpath(dirs.DataIn);               % Add dir w/ your Data path
addpath(genpath(dirs.Code));        % Add dir w/ your code path
addpath(genpath(dirs.PTB));         % Add dir w/PsychToolbox code
addpath(genpath(dirs.chronux));     % Add dir w/chronux code

end
