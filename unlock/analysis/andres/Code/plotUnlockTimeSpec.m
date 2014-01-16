function hFig = plotUnlockTimeSpec(unlockData,specData,SpecInfo,unlockInfo)
%
%
%
%
%
%

% Params
nChs    = unlockInfo.main.nChs;
chStart = unlockInfo.plot.chStart;          % first index for plotted channels. 2-4 for O1,Oz,O2
chEnd   = unlockInfo.plot.chEnd;            % last index for plotted channels 
freq1   = unlockInfo.plot.freq1 + 1;        % Add 1 since Freq. vals start in zero. lower bound frequency.
freq2   = unlockInfo.plot.freq2;            % higher bound frequency

if unlockInfo.plot.harmoNum == 1;           % harmonics to plot. Zero for basic frequency. 1 for first harmonic.
    freq1 = 19;
    freq2 = 40;
    disp([freq1  freq2])
elseif unlockInfo.plot.harmoNum == 0;       % harmonics to plot. Zero for basic frequency. 1 for first harmonic.
   
else
    warning('Problems with the harmonics plotted!!!')
end

windSz  = unlockInfo.plot.windSz;           % Size of plotted window
movWind = unlockInfo.plot.movWind;          % Size of window moves
typePlot = unlockInfo.plot.typePlot;        % Type of plot
lagVal = 0.4;
warning('LAG!!!!')

% Data
eegData     = unlockData.data;
eegTime     = 0:1/unlockInfo.main.Fs:unlockInfo.main.len;
eegDcdTgt   = unlockData.dcdTgt;
fspec       = specData.fspec;
tspec       = specData.tspec;

hFig = figure;
%% Plotting
switch typePlot
    case 'specEpoch'
        warning('Plot only the Oz, O1 and O2 channels'), avrage and single trial, check matched decoded.
        get decoder from this.
        specData.data()
        
    case 'spectAll'
    %% Subplot all
       	set(hFig,'Position',[ 399    49   901   768],'visible','on')
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
        for iCh = 1:nChs
            subplot(4,2,iCh)
            plot(fspec(fStart:fEnd),squeeze(specData.data(fStart:fEnd,iCh)))
            set(gca,'Ydir','normal')
            title(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
            ylabel('Freq. power'), xlabel('Freq. [Hz]'), axis tight
        end       
        
    case 'specAll'
        %% Subplot all
       	set(hFig,'Position',[ 399    49   901   768],'visible','on')
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
        for iCh = 1:nChs
            subplot(4,2,iCh)
            imagesc(tspec,fspec(fStart:fEnd),squeeze(specData.data(:,fStart:fEnd,iCh)'))
            set(gca,'Ydir','normal')
            title(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
            xlabel('Time [s]'), ylabel('Freq. [Hz]')
        end
       
    case 'specOrganizado!!!'
        set(hFig,'Position',[399 49 560 768])
        %% Subplot all with decoder targets
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
        for ii = 1:round(movWind*SpecInfo.sec2spec):length(tspec)
            % Start and end times converted to spec samples
            tStart = ii;
            tEnd = ii + round(windSz*SpecInfo.sec2spec);
            % converted to time samples
            rawStart = round((ii/SpecInfo.sec2spec)*unlockInfo.main.Fs);
            rawEnd = round((windSz + ii/SpecInfo.sec2spec)*unlockInfo.main.Fs);
            % Plot each channel
            kk = 0;
            for iCh = chStart:chEnd
                kk = kk + 1;
                subplot(chEnd-chStart+1,1,kk)
                hold off
                imagesc(tspec(tStart:tEnd),fspec(fStart:fEnd),squeeze(specData.data(tStart:tEnd,fStart:fEnd,iCh)'))
                set(gca,'Ydir','normal')
                hold on
                plot(eegTime(rawStart:rawEnd),eegDcdTgt(rawStart:rawEnd),'lineWidth',unlockInfo.plot.lineWidth,'Color',unlockInfo.plot.colors(1,:))
                xlabel('Time [s]'), ylabel(sprintf('%s [Hz]',unlockInfo.main.elecLoc{iCh}),'FontWeight','Bold')
            end
            pause
        end
     
    case 'specDcdTgt'
        set(hFig,'Position',[131 49 1355 768])
        %% Subplot all with decoder targets
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
        for ii = 1:round(movWind*SpecInfo.sec2spec):length(tspec)
            % Start and end times converted to spec samples
            tStart = ii;
            tEnd = ii + round(windSz*SpecInfo.sec2spec);
            % converted to time samples
            rawStart = round((lagVal+ii/SpecInfo.sec2spec)*unlockInfo.main.Fs);
            rawEnd = round((windSz + ii/SpecInfo.sec2spec)*unlockInfo.main.Fs);
            % Plot each channel
            kk = 0;
            for iCh = chStart:chEnd
                kk = kk + 1;
                subplot((chEnd-chStart + 1)*2+1,1,[kk*2-1 kk*2])
                imagesc(tspec(tStart:tEnd),fspec(fStart:fEnd),squeeze(specData.data(tStart:tEnd,fStart:fEnd,iCh)'))
                set(gca,'Ydir','normal')
                xlabel('Time [s]'), ylabel(sprintf('%s [Hz]',unlockInfo.main.elecLoc{iCh}),'FontWeight','Bold')
            end
            subplot((chEnd-chStart + 1)*2+1,1,(chEnd-chStart+1)*2+1)
            plot(eegTime(rawStart:rawEnd),eegDcdTgt(rawStart:rawEnd),'lineWidth',unlockInfo.plot.lineWidth,'Color',unlockInfo.plot.colors(1,:))
            ylabel('DcdTgt','FontWeight','Bold');
            axis tight;
            warning('Axis in time and freq. shifted!!!')
            pause
        end
        
    case 'eachAllSpec'
        %% Plot each/pause
        for iCh = 1:nChs
            imagesc(tspec,fspec(fStart:fEnd),squeeze(specData.data(:,fStart:fEnd,iCh)'))
            set(gca, 'YDir', 'normal');
            title(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
            xlabel('Time [s]'), ylabel('Freq. [Hz]')
            pause;
        end
        
    case 'specWindow'
        %% Plot O1,Oz,O2 (2:4)
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
        for ii = 1:round(movWind*SpecInfo.sec2spec):length(tspec)
            % Start and end times converted to samples
            tStart = ii;
            tEnd = ii + round(windSz*SpecInfo.sec2spec);
            % Plot each channel
            kk = 0;
            for iCh = chStart:chEnd
                kk = kk + 1;
                subplot(chEnd-chStart+1,1,kk)
                imagesc(tspec(tStart:tEnd),fspec(fStart:fEnd),squeeze(specData.data(tStart:tEnd,fStart:fEnd,iCh)'))
                set(gca,'Ydir','normal')
                title(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
                xlabel('Time [s]'), ylabel('Freq. [Hz]')
            end
            pause
        end
        
    case 'onlyOs'
                %% Plot O1,Oz,O2 (2:4)
        fStart  = round(freq1*SpecInfo.hz2spec);   % Lower frequency bound
        fEnd    = round(freq2*SpecInfo.hz2spec);  % Higher freq. bound
        
%         %Find O1,Oz and O2
%         strcmpi(unlockInfo.main.elecLoc,'o1')

        
    case 'timeWindow'
        %% Time domain plots
        for ii = 1:round(movWind*unlockInfo.main.Fs):length(eegData)
            % Start and end times converted to samples
            tStart = ii;
            tEnd = ii + round(windSz*unlockInfo.main.Fs);
            %fprintf('%i-%i-%i\n',[tStart tEnd ii])
            % Plot each channel
            kk = 0;
            for iCh = chStart:chEnd
                kk = kk + 1;
                subplot(chEnd-chStart+1,1,kk)
                plot(eegTime(tStart:tEnd),eegData(tStart:tEnd,iCh))
                %title(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
                ylabel(unlockInfo.main.elecLoc{iCh},'FontWeight','Bold')
                xlabel('Time [s]'),
                ylim([-0.8 0.8])
                axis tight
            end
            pause
        end
        
        
        % Decoded targets using the HSD
        % indx = find(unlockData.dcdTgt);
        % dcdTgt = unlockData.dcdTgt(indx);
        %
        % unlockInfo.main.elecLoc
        %
        % totalTime = unlockInfo.main.szData(1)/unlockInfo.main.Fs;
        
    case 'diagnostic'
        %% Diagnostic of location of end of trial flags
        hFig = figure;
        for iChs = 1:nChs
            subplot(nChs,1,iChs)
            plot(endTrials(:,iChs))
            %title(sprintf('Channel %i',iChs))
            ylabel(sprintf('Ch%i',iChs))
        end
        subplot(nChs,1,1)
        title(sprintf('Location of endTrialFlag %i in recording',endTrialFlag),'FontWeight','Bold')
end

% [row,colm] = find();
% loco = sum(sum())x
% 
% % Fi
% for ii = 1:BCIinfo.numChs       %total number of EEG channels
%     figure(1000+ii), imagesc(tspec,fspec,10*log((abs(flipud(squeeze((specData.data(:,:,ii)))')))));
%     title(sprintf('Ch %i',chs(ii)));
% end


%% 
% % Figure for?
% function plotSpec(allTgtMeanSpec,allTgtSpecInfo,plotInfo)
% %
% %
% %
% %
% %
% %
% 
% %% Plotting each channels
% for Ch = 1:size(allTgtMeanSpec,3)
%     figure(Ch);
%     set(gcf, 'Position', get(0,'Screensize'),'PaperPositionMode','auto','Visible','Off');
%     disp(sprintf('Plotting Ch %03d',Ch));
% 
%     % Plotting each target
%     for Tgt = 1:length(plotInfo.targets)
%         % Vbles used to plot
%         plotInfo.TgtPlot.Tgt = Tgt;
%         plotInfo.plotChClim = plotInfo.plotClims(Ch).vals;
%         plotInfo.plotCh = Ch;
%         SpecInfo = allTgtSpecInfo(Tgt).info;
%         meanSpec = squeeze(allTgtMeanSpec(:,plotInfo.plotFband(1):plotInfo.plotFband(2),Ch,Tgt));
%         
%         %% Plotting Spectrogram
%         hold off
%         subplot(plotInfo.TgtPlot.rows,plotInfo.TgtPlot.colms,[plotInfo.TgtPlot.subplot{plotInfo.TgtPlot.Tgt},(plotInfo.TgtPlot.subplot{plotInfo.TgtPlot.Tgt})+plotInfo.TgtPlot.colms,(plotInfo.TgtPlot.subplot{plotInfo.TgtPlot.Tgt})+2*plotInfo.TgtPlot.colms,(plotInfo.TgtPlot.subplot{plotInfo.TgtPlot.Tgt})+3*plotInfo.TgtPlot.colms]);
%         if plotInfo.useClims        %Using clims
%             if plotInfo.normF       %Normalizing spectrograms
%                 imagesc(plotInfo.tspec,plotInfo.plotFspec,(abs(flipud((plotInfo.plotNormf.*meanSpec)'))),plotInfo.plotChClim);
%             else
%                 imagesc(plotInfo.tspec,plotInfo.plotFspec,10*log(abs(flipud(meanSpec'))),plotInfo.plotChClim);
%             end
%         else                        %No clims used
%             if plotInfo.normF       %Normalizing spectrograms
%                 imagesc(plotInfo.tspec,plotInfo.plotFspec,(abs(flipud((plotInfo.plotNormf.*meanSpec)'))));
%             else
%                 imagesc(plotInfo.tspec,plotInfo.plotFspec,10*log(abs(flipud(meanSpec'))));
%             end
%         end
%         colorbar
%         %% Delay On/Offset 
%         hold on,line(xDelayOn,yDelayOn,'color','k','lineWidth',3,'lineStyle','--')
%         hold on,line(xDelayOff,yDelayOff,'color','k','lineWidth',3,'lineStyle','--')
% 
%         %% Axis properties
%         % x axis labels
%         xlabels = get(gca,'xticklabel');
%         set(gca,'xticklabel',xlabels);
%         numXlabel = num2str(str2num(xlabels) - preStart/1000);      %changing values to match DelayOnset
%         set(gca,'xticklabel',numXlabel);
%         ylabels = str2num(get(gca,'yticklabel'));
%         numYlabels = num2str(flipud(ylabels));
%         % y axis labels
%         set(gca,'yticklabel',numYlabels)
%         xlabel('Seconds','Fontsize',10,'FontWeight','bold')
%         if plotInfo.normF
%             ylabel('Hz (F norm)','Fontsize',10,'FontWeight','bold')
%         else
%             ylabel('Hz (dB)','Fontsize',10,'FontWeight','bold')
%         end
%     end
%     
%     %% Saving figures
%     ThisCh = sprintf('Ch%03d',Ch);
%     if Ch == 1
%         preCh = 'Ch001';
%         plotInfo.dirs.saveFile = strrep(plotInfo.dirs.saveFile,'AllChs',ThisCh);
%     else
%         preCh = sprintf('Ch%03d',Ch-1);
%         plotInfo.dirs.saveFile = strrep(plotInfo.dirs.saveFile,preCh,ThisCh);
%     end
%     title(sprintf('%s-%s-%s',ThisCh,plotInfo.titleFreqs,plotInfo.plotTitle));
%     saveas(gcf,fullfile(plotInfo.dirs.saveFolder,plotInfo.dirs.saveFile));delete(gcf);
% end
% 





