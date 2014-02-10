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
        dirs.BCIparams  = '';                                                       % Add path where all BCIparams are located
        dirs.PTB        = 'C:\Users\salacho\Documents\MATLAB\toolbox\Psychtoolbox'; % Add path to PsychToolbox
        dirs.chronux    = 'C:\Users\salacho\Documents\MATLAB\toolbox\chronux';      % Add path to chronux toolbox
    case 'Salachos-Carbon'
        dirs.Code       = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Code\analysis'; % Dir w/ data analysis Code
        dirs.helpers    = '';                                                                   % Dir w/ helpers analysis Code
        dirs.DataIn     = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\raw';      % Dir w/ datafiles. Mapping server using SFTP Net Drive
        dirs.DataOut    = 'C:\Users\Administrator\Documents\BU\Speechlab\Unlock\Data\mat';      % Local Dir to output analyzed datafiles and figures too
        dirs.BCIparams  = '';                                                                   % Add path where all BCIparams are located
        dirs.PTB        = '';                                                                   % Add path to PsychToolbox
        dirs.chronux    = 'C:\Users\Administrator\Documents\MATLAB\Chronux_matlab\chronux_code_2_00\chronux';      % Add path to chronux toolbox
    otherwise
        error('No paths have been estalished!')
end

% Set up path so code is accessible to Matlab
addpath(dirs.helpers);              % Add dir w/ my helpers
addpath(dirs.DataIn);               % Add dir w/ your Data path
addpath(genpath(dirs.Code));        % Add dir w/ your code path
addpath(genpath(dirs.PTB));         % Add dir w/PsychToolbox code
addpath(genpath(dirs.chronux));     % Add dir w/chronux code
