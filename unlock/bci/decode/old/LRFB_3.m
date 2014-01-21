 function LRFB_3()

% Version 3: added calculations for thresholds from the calibration,
% changed sample/data rate, changed timer

daqreset;
delete(timerfindall);
clear all; close all;

options = paramSetupLRFB; % pulls up GUI

% CHANGE EACH TIME
subject_id = options.subject_ID;
calibration1 = options.calibration1;
calibration2 = options.calibration2;
block = options.block;
cohort = 'CY';

% timing definitions
sampleRate = 4000; % Hz
dataRate = 12; % Hz
filter_alpha = .95;

% interface with nidaq or winsound (guessing)
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


% % for loop to plot data, RMF, filter for each channel
% h_fig = figure;
% for i=1:length(options.ai)
%     subplot(length(options.ai),1,i)
%     h_raw(i) = plot(0,0,'b'); hold on;
%     h_rms(i) = plot(0,0,'r:');
%     h_filt(i) = plot(0,0,'g--');
%     h_text(i) = text(0,0,'','HorizontalAlignment','center');
%     title(['Channel ',num2str(options.ai(i))])
%     legend('Raw data','RMS','Filtered')
% end

commands = {'Left','Right','Forward','Backward'};
nTrials = 12; % should be divisible by 4

nListReps = ceil(nTrials/length(commands));
command_list = repmat(commands',nListReps,1);
command_list = command_list(1:nTrials);

% randomizes
reorder_idx = randperm(size(command_list,1));
command_list = command_list(reorder_idx,:);

win = 1; % 0 is default
%dims = [0 0 500 500]; % [left top right bottom] , optional input

% 0-255, lower value = darker, scalar is greyscale, 3 element vector is [R G B]
bkg_color = 0;
wait_color = 255;
go_color = [0 150 0];

% calculates threshold from average of 2 best calibrations
load(sprintf('LRFBcalibration_%s%d_%d.mat',cohort,subject_id,calibration1));
l_threshold = max(draw_rms(:,1));
r_threshold = max(draw_rms(:,2));
f_threshold = max(draw_rms(:,3));
wink_threshold = max(draw_rms(:,4));

load(sprintf('LRFBcalibration_%s%d_%d.mat',cohort,subject_id,calibration2));
l_threshold = (l_threshold + max(draw_rms(:,1)))/2 *.30;
r_threshold = (r_threshold + max(draw_rms(:,2)))/2 *.30;
f_threshold = (f_threshold + max(draw_rms(:,3)))/2 *.50;
wink_threshold = (wink_threshold + max(draw_rms(:,4)))/2 *.50;



% for bit calculations later
nChoices = length(commands);
nCorrect = 0;
total_t = 0;


% STARTING
[wPtr, rect] = Screen('OpenWindow',win,bkg_color,dims);

Screen('TextSize',wPtr, 72);
DrawFormattedText(wPtr,'Start','center','center',wait_color);
Screen(wPtr,'Flip');
tic;
while toc < 2
end


for i = 1:nTrials
    
    all_data = zeros(1,4);
    all_t = [];
    draw_t = [];
    draw_rms = zeros(1,4);
    draw_y = [];
    
    
    Screen('TextSize',wPtr, 72);
    DrawFormattedText(wPtr,char(command_list(i)),'center','center',wait_color);
    Screen(wPtr,'Flip');
    tic;
    while toc < 2
    end
    
    Screen('TextSize',wPtr, 72);
    DrawFormattedText(wPtr,char(command_list(i)),'center','center',go_color);
    t_start = Screen(wPtr,'Flip');
    tic;
    start(ai);
    t = 0;
    while isrunning(ai) && max(draw_rms(:,4)) < wink_threshold
        
        [emg_data,emg_t] = getdata(ai,actualRate/dataRate);
        
        t = toc;
        %concatenate all data
        all_data = [all_data; emg_data];
        all_t = [all_t; emg_t];
        
        draw_t = [draw_t; t];
        if ~exist('draw_rms','var')
            draw_rms = [];
        end
        draw_rms = [draw_rms; zeros(1,size(emg_data,2))];
        for j=1:length(options.ai)
            draw_rms(end,j) = sqrt(mean(emg_data(:,j).^2));
            % draw_rms = [draw_rms; sqrt(mean(emg_data(:,1).^2)) sqrt(mean(emg_data(:,2).^2))];
        end
        if ~isempty(draw_y)
            draw_y = [draw_y; filter_alpha*draw_y(end,:) + (1-filter_alpha)*(draw_rms(end,:))];
        else
            draw_y = draw_rms(end,:);
        end
    end
    
    given_command = command_list(i);
    stop(ai);
    
    nSamples = length(draw_rms);
    window_idx = floor(nSamples*.20);
    if window_idx == 0
        window_idx = 1;
    end
    window = draw_rms(window_idx:end,:);
    % classifier
    if ((max(window(:,1)))> l_threshold) && ((max(window(:,2)))< r_threshold) && ((max(window(:,3)))< f_threshold)
        movement = 'Left';
    elseif (max(window(:,1))< l_threshold) && (max(window(:,2))> r_threshold)&&(max(window(:,3))< f_threshold)
        movement = 'Right';
    elseif (max(window(:,1))> l_threshold) && (max(window(:,2))>r_threshold) && (max(window(:,3))> f_threshold)
        movement = 'Forward';
    elseif (max(window(:,1))> l_threshold) && (max(window(:,2))> r_threshold) && (max(window(:,3))< f_threshold)
        movement = 'Backward';
    else
        movement = 'Unknown';
    end
    
    
    Screen('FillRect',wPtr,bkg_color);
    t_end = Screen(wPtr,'Flip');
    tic;
    while toc < 1
    end

    all_data = all_data(2:end,:);
    draw_rms = draw_rms(2:end,:);
    
    save(sprintf('LRFBtrial_%s%02d_%02d_%02d.mat',cohort,subject_id,block,i),'all_t','all_data','draw_t','draw_rms','draw_y','given_command','movement','window','l_threshold','r_threshold','f_threshold','wink_threshold');
    
    if strcmp(given_command,movement)
        nCorrect = nCorrect + 1;
        Screen('TextSize',wPtr, 60);
        DrawFormattedText(wPtr,sprintf('Correct!\nYour direction: %s',movement),'center','center',wait_color);
        Screen(wPtr,'Flip');
        tic;
        while toc<2
        end
    else
        Screen('TextSize',wPtr, 60);
        DrawFormattedText(wPtr,sprintf('Incorrect.\nYour direction: %s',movement),'center','center',wait_color);
        Screen(wPtr,'Flip');
        tic;
        while toc<2
        end
    end

    total_t = total_t + (t_end - t_start);
    
end

Screen('FillRect',wPtr,bkg_color);
Screen(wPtr,'Flip');
tic;
while toc < 1
end

percent_accurate = nCorrect/nTrials;
if percent_accurate == 1
    percent_accurate = 0.9999999;
end
selections_min = nTrials/(total_t/60); % selections per minute
bpselection = log2(nChoices) + percent_accurate*log2(percent_accurate) + (1-percent_accurate)*log2((1-percent_accurate)/(nChoices-1));
bpminute = bpselection*selections_min;

save(sprintf('LRFBscore_%s%02d_%02d.mat',cohort,subject_id,block),'total_t','percent_accurate','selections_min','bpselection','bpminute');

Screen('TextSize',wPtr, 60);
DrawFormattedText(wPtr,'Done!\n \n','center','center',wait_color);
Screen(wPtr,'Flip');
tic;
while toc < 1
end

Screen('TextSize',wPtr, 60);
DrawFormattedText(wPtr,sprintf('Done!\nPercent accurate: %g %% \n',percent_accurate*100),'center','center',wait_color);
Screen(wPtr,'Flip');
tic;
while toc < 1
end

Screen('TextSize',wPtr, 60);
DrawFormattedText(wPtr,sprintf('Done!\nPercent accurate: %g %% \nYour score: %g',percent_accurate*100,bpminute),'center','center',wait_color);
Screen(wPtr,'Flip');
tic;
while toc < 3
end


Screen('CloseAll');

end












