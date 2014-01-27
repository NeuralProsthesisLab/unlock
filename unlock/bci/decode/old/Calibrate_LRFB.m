                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
function Calibrate_LRFB()

daqreset;
delete(timerfindall);
clear all; close all;

options = paramSetup;

% timing definitions
sampleRate = 4000; %Hz
dataRate = 12; %Hz
filter_alpha = .95;

if ~isempty(findstr('nidaq',options.aidevice_name))
    ai = analoginput('nidaq','Dev1');
    addchannel(ai, options.ai);
    set(ai,'InputType','SingleEnded');
    actualRate = setverify(ai,'SampleRate',sampleRate);
    ai.SamplesPerTrigger = Inf;
    set(ai,'LoggingMode','Memory')
    setverify(ai.Channel,'InputRange',[-5 5]);
elseif ~isempty(findstr('winsound',options.aidevice_name))
    ai = analoginput('winsound',0);
    addchannel(ai, options.ai);
    actualRate = setverify(ai,'SampleRate',sampleRate);
    ai.SamplesPerTrigger = Inf;
else
    return;
end
      
        
h_fig = figure;
for i=1:length(options.ai)
    subplot(length(options.ai)+1,1,i)
    h_raw(i) = plot(0,0,'b'); hold on;
    h_rms(i) = plot(0,0,'r:');
    h_filt(i) = plot(0,0,'g--');
    h_text(i) = text(0,0,'','HorizontalAlignment','center');
    title(['Channel ',num2str(options.ai(i))])
    legend('Raw data','RMS','Filtered')
end
subplot(length(options.ai)+1,1,length(options.ai)+1)
h_key = plot(0,0);
title('Keypress')
set(gcf,'KeyPressFcn',@(h_obj,evt) ProcessKeyboard(h_obj,evt));
keypress = 0;

% all_length = 100*actualRate;
% all_data = zeros(all_length,2);
% all_t = zeros(all_length,1);
% 
% draw_length = 100*dataRate;
% draw_t = zeros(draw_length,1);
% draw_rms = zeros(draw_length,2); draw_y = zeros(draw_length,2);
% draw_keypress = zeros(draw_length,1);
all_data = []; 
all_t = [];
draw_t = [];
draw_rms = [];
draw_y = [];
draw_keypress = [];

texthandle = text(0,0,'Press any key to begin','HorizontalAlignment','center');

%pause()  %does not work well in MATLAB 7.4 because of window focus problems
% use this instead
waiting = 1;
while(waiting)
    drawnow
end

set(texthandle,'String','Collecting- logging keystrokes.  Esc to quit');

tic; % now we start
t = 0;
start(ai)
running = 1;
while isrunning(ai) && running
    % get EMG data (this blocks until it gets the data it wants)
    
    [emg_data,emg_t] = getdata(ai,actualRate/dataRate);

    % if you want to FAKE
    %emg_data = [.5 + .5*sin(emg_t) .5 + .5*cos(emg_t)]; 
    
    t = toc;
    %concatenate all data
    all_data = [all_data; emg_data];
    all_t = [all_t; emg_t];

    draw_t = [draw_t; t];
    draw_keypress = [draw_keypress; keypress]; keypress = 0; % handle any keypress
    if ~exist('draw_rms','var')
        draw_rms = [];
    end
    draw_rms = [draw_rms; zeros(1,size(emg_data,2))];
    for i=1:length(options.ai)
        draw_rms(end,i) = sqrt(mean(emg_data(:,i).^2));
%         draw_rms = [draw_rms; sqrt(mean(emg_data(:,1).^2)) sqrt(mean(emg_data(:,2).^2))];
    end
    if ~isempty(draw_y)
        draw_y = [draw_y; filter_alpha*draw_y(end,:) + (1-filter_alpha)*(draw_rms(end,:))];
    else
        draw_y = draw_rms(end,:);
    end
end
stop(ai)

% delete(texthandle);
for i=1:length(options.ai)
    set(h_raw(i),'XData',all_t,'YData',all_data(:,i))
    set(h_rms(i),'XData',draw_t,'YData',draw_rms(:,i))
    set(h_filt(i),'XData',draw_t,'YData',draw_y(:,i))    
    set(h_text(i),'Position',[mean(all_t) mean(all_data(:,i)) 0],...
        'HorizontalAlignment','center',...
        'String',['Max RMS= ' num2str(max(draw_rms(:,i))) '  Max Filtered=',num2str(max(draw_y(:,i)))])
    fprintf(['\nChannel ',num2str(options.ai(i)) '\nMax RMS= ' num2str(max(draw_rms(:,i))) '\nMax Filtered=' num2str(max(draw_y(:,i))) '\n\n'])
end
set(h_key,'XData',draw_t,'YData',draw_keypress);
drawnow;

[file,path] = uiputfile('LRFBcalibration_###.mat','Save Calibration File As:');
save(fullfile(path,file),'all_t','all_data','draw_t','draw_rms','draw_y','draw_keypress');

    function [] = ProcessKeyboard(foo,evt)
        keypress = 1;
        if strmatch(evt.Key,'escape','exact')
            running = 0;
        end
        if (waiting)
            waiting = 0 ;
        end
    end
end