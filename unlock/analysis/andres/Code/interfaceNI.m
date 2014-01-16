function interfaceNI
%
%
%
%
%
%
%
%


niConfigParams = setNIcardConfigParams;


%% Display devices and select the USB-NI card
allDevices = daq.getDevices;
if length(allDevices) > 1
    tgtDev = allDevices(devNumber);
    disp(tgtDev)
else
    tgtDev = allDevices(1);
    disp(tgtDev);
end

%% Create NI recording session and add Analog Input Channels (from niChsID) from device niDevID to the session.
if niConfigParams.doAnalogInChns
    niSession = daq.createSession('ni');
    niCh(1) = niSession.addAnalogInputChannel(niConfigParams.niDevID,niConfigParams.niAIchsID(1), 'Voltage');
    niCh(2) = niSession.addAnalogInputChannel(niConfigParams.niDevID, niConfigParams.niAIchsID(2), 'Voltage');
end

niSession.Rate = niConfigParams.niSampRate;                         % NI card sampling rate
niSession.DurationInSeconds = niConfigParams.recordDurationInSec;   % total length of recording in seconds
% All channels at same ADC resolution
niSession.Channels(:).Range = niConfigParams.ChsValRange;              % NI ADC range of input data [Min. Max.], can be [-10 10]
niSession.Channels(:).TerminalConfig = niConfigParams.TerminalConfig;                % Type of recording with respect to GND. Can be 'Differential', 'SingleEnded', 'SingleEndedNonReferenced', 'PseudoDifferential'.


% create a counter channel
if niConfigParams.doCounterInChns
    % To add a counter channel, to count photodiode activity
%    niCh(3) = niSession.addCounterInputChannel(niDevID, niCountChs(2),)
end





if niConfigParams.doAnalogOutChns

niSession.addAnalogOutputChannel(niConfigParams.niDevID,0,'Current')

Create a digital input and output object and add a digital input line.	

dio = digitalio('nidaq','Dev1'); 
addline(dio,0:3,'in');

	

s = daq.createSession('ni'); 
s.addDigitalChannel('Dev1', 'Port0/Line0:1', 'InputOnly');

Create counter input channels	You cannot use counter channels in the legacy interface.	

s = daq.createSession ('ni') 
s.addCounterInputChannel('Dev1','ctr0','EdgeCount')



%% Collect a single scan
% data = niSession.inputSingleScan;

%% Record data
[data,time] = niSession.startForeground;

plot(time,data);
xlabel('Time (secs)');
ylabel('Voltage')


%% Trigger photodiode to start recording after first flash.
%niSession.IsWaitingForExternalTrigger = true;

