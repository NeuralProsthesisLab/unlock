function niConfigParams = setNIcardConfigParams(devNumber)
% function niConfigParams = setNIcardConfigParams(devNumber)
% 
% Set the configuration parameters for the National Instrument card. Right
% now works for the USB NI-62118. 
%
% INPUT:
% devNumber:        integer. Device number in the list found by the 
%                   "daq.getDevices" command. It is 1 by default.
% OUTPUT
% niConfigParams:   structure with all fields to set the configuration of
%                   the NI card. This parameters are used by
%                   "configureNIcard.m".
%
% Created 15 Jan 2014
% Last modified 22 Jan 2014
% Andres v.1

%% NI Configuration Parameters
%posIndx = strcmpi(tgtDev,'USB-6218 (Device ID:');      Need to find a way to find the card, automatically, and use it to select the proper device. 
% Device and channels form the NI card
niConfigParams.devNumber    = devNumber;            % Device number from al the list of devices in the computer
if niConfigParams.devNumber == 1    
    niConfigParams.devID  = 'dev1';       % name of the NI USB-6218 device in Andres' laptop
else
    warning('Device number not recognized!!!')    
end

% Get total number of channels to read from
niConfigParams.numAIchs     = 1;            % Number of analog input channels (up to 32 in USB-6218
niConfigParams.numAOchs     = 1;            % Number of analog output channels (up to 2 in USB-6218
niConfigParams.numDIchs     = 2;            % Number of digital input channels (up to 32 in USB-6218
niConfigParams.numDOchs     = 1;            % Number of digital output channels (up to 32 in USB-6218
niConfigParams.numCIOchs 	= 2;            % Number of input/output counters

% Set channels and digital ports
niConfigParams.AIchsID      = 0:7;          % Select chID of analog input channels (up to 32 in USB-6218
niConfigParams.AOchsID      = 0:1;          % Select chID of analog output channels (up to 2 in USB-6218
niConfigParams.DIlines      = 0;          % Select chID of digital input channels (up to 32 in USB-6218
niConfigParams.DOlines      = 0:7;          % Select chID of digital output channels (up to 32 in USB-6218

% niConfigParams.DIchsID = '';                % channel ID
% niConfigParams.DOchsID = '';

niConfigParams.numDIports = 1;              % Number of DI ports
niConfigParams.numDOports = 1;              % Number of DO ports

% Define ports
% Sets ports in order, starting from DI, then DO
for iDIport = 1:niConfigParams.numDIports
    if length(niConfigParams.numDIchs) == 1
        % For only 1 line in one port
        %niConfigParams.DIchsID(iDIport) = sprintf('port0/line0:3');       % four lines (0:3) in port0
        niConfigParams.DIchsID{iDIport} = sprintf('Port%i/Line%i',iDIport-1,niConfigParams.DIlines(1));       % four lines (0:3) in port0
    else
        % For several lines in same port
        niConfigParams.DIchsID{iDIport} = sprintf('Port%i/Line%i:',iDIport-1,niConfigParams.DIlines(1),niConfigParams.DIlines(end));       % four lines (0:3) in port0
    end
end

% Set ports for the counters. Only wo available for both input and output for USB NI-6218: 'ctr0','ctr1'
niConfigParams.CIOchsID   = 0:1;         % Select chID of the counter input/output

%Counter measurement types. 'EdgeCount' the most common for now 
% 'EdgeCount','PulseWidth','Frequency','Position' 
niConfigParams.CImeasType = 'EdgeCount';

% Channel properties
niConfigParams.SampRate 	= 1000;     	% NI card sampling rate

% Type of recording, continuous or for a set time 
niConfigParams.IsContinuous = true;             % logical. True to stop only when 'stop' flag is used (daq.Session.stop).
if ~niConfigParams.IsContinuous 
    niConfigParams.recordDurationInSec = 10; 	% double. Duration of data recording in seconds

end

niConfigParams.ChsValRange  = [-5 5];           % Vector. [Min. Max.] Range of the input data. Can be also [-10 10]
niConfigParams.TerminalConfig = 'SingleEnded';  % Will apply to all channels. Type of terminal recording configuration with respect to GND and other channels. Can be 'Differential', 'SingleEnded', 'SingleEndedNonReferenced', 'PseudoDifferential'.

% Logical flags to use channels
niConfigParams.doAnalogInChns   = true;     % logical. Set up NI analog input channels to read from them
niConfigParams.doAnalogOutChns  = false;     % logical. Set up NI analog output channels to pull data from them
niConfigParams.doDigitInChns    = false;     % logical. Set up NI digital input channels to read data from them
niConfigParams.doDigitOutChns   = false;     % logical. Set up NI digital output channels to pull data from them
niConfigParams.doCounterInChns 	= false; 	% logical. Set up NI counter channels to read from them
niConfigParams.doCounterOutChns = false; 	% logical. Set up NI counter channels to pull data from them
niConfigParams.doPhotoDiode     = false;     % Simple code for photodiode data
niConfigParams.doClockCh        = false;     % logical. Sets a ni NI session for a clocked signal (for digital input/output channels)

if niConfigParams.doDigitInChns 
    niConfigParams.doClockCh = true;
    warning('Any digital input/output needs a clock!!')
end
% Internal clock required for digital input/output
niConfigParams.clockFreq = niConfigParams.SampRate;

% Set action 
niConfigParams.doBackground = true;         % run commands and collect data in the background. Opposite to niConfigParams.doForegroung = false;

%% Only allow NI card for photoDiode recordings (for now, to avoid mixing port and lines)
if niConfigParams.doPhotoDiode
    niConfigParams.doAnalogInChns   = false;     % logical. Set up NI analog input channels to read from them
    niConfigParams.doAnalogOutChns  = false;     % logical. Set up NI analog output channels to pull data from them
    niConfigParams.doDigitInChns    = false;     % logical. Set up NI digital input channels to read data from them
    niConfigParams.doDigitOutChns   = false;     % logical. Set up NI digital output channels to pull data from them
    niConfigParams.doCounterInChns 	= false; 	% logical. Set up NI counter channels to read from them
    niConfigParams.doCounterOutChns = false; 	% logical. Set up NI counter channels to pull data from them
    niConfigParams.doPhotoDiode     = true;     % Simple code for photodiode data
    niConfigParams.doClockCh        = false;     % logical. Sets a ni NI session for a clocked signal (for digital input/output channels)
end 

% niSession.startForeground()
% niSession.startBackground()

