function niConfigParams = setNIcardConfigParams
% function niConfigParams = setNIcardConfigParams
%
% 
%
%
%
% Created 15 Jan 2014
% Last modified 15 Jan 2014
% Andres v.1

%% NI Configuration Parameters
%posIndx = strcmpi(tgtDev,'USB-6218 (Device ID:');      Need to find a way to find the card, automatically, and use it to select the proper device. 
% Device and channels form the NI card
niConfigParams.devNumber    = 1;            % Device number from al the list of devices in the computer
niConfigParams.niDevID      = 'dev1';       % name of the NI USB-6218 device in Andres' laptop

niConfigParams.niAIchsID    = 0:7;        % Select number of analog input channels (up to 32 in USB-6218
niConfigParams.niAOchsID    = 0:1;        % Select number of analog output channels (up to 2 in USB-6218
niConfigParams.niDIchsID    = 0:7;        % Select number of digital input channels (up to 32 in USB-6218
niConfigParams.niDOchsID    = 0:7;    	% Select number of digital output channels (up to 32 in USB-6218

niConfigParams.niCountsID   = 0:1;         % Counter

niConfigParams.niSampRate 	= 10000;        % NI card sampling rate
niConfigParams.recordDurationInSec = 10;    % double. Duration of data recording in seconds
niConfigParams.ChsValRange  = [-5 5];       % Vector. [Min. Max.] Range of the input data. Can be also [-10 10]
niConfigParams.TerminalConfig = 'SingleEnded';  % Type of terminal recording configuration with respect to GND and other channels. Can be 'Differential', 'SingleEnded', 'SingleEndedNonReferenced', 'PseudoDifferential'.



niConfigParams.doAnalogInChns   = true;     % logical. Set up NI analog input channels to read from them
niConfigParams.doCounterInChns 	= true; 	% logical. Set up NI counter channels to read from them




