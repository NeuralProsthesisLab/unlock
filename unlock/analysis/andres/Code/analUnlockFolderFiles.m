function unlockFiles = analUnlockFolderFiles
% function analUnlockFolderFiles
%
%
%
%
% Andres v.1
% Created 07 Jan 2014
% Last modified 07 Jan 2014

codePath = pwd;         % code path
filesFolder = 'C:\Users\Administrator\Documents\BU\Speechlab\unlock\data\raw\20140106-mobilab';
cd(filesFolder)
fileList = dir;         % list of files
cd(codePath)            % returning to code folder

%% Calculating plots for each file
xLabelStr{1} = '-';
ii = 0;
for iFile = 3:14
    ii = ii + 1;
    fprintf('Working on file %s...\n',iFile)
    fileName = fullfile(filesFolder,fileList(iFile).name);
	onlinePerf = unlockMain(fileName);
    onlinePerf.fileName = fileName;
    unlockFiles(ii) = onlinePerf;
    close all
    str2comp = 'mobilab-single-ssvep-diag-';
    lenStr = length(str2comp);
    strIndx = strfind(onlinePerf.fileName,str2comp);
    xLabelStr{ii+1} = onlinePerf.fileName(strIndx+lenStr:strIndx+lenStr+3);
end

% Plot performances
hFig = plot([unlockFiles(:).overallf],'b','LineWidth',2);
hold on
plot([unlockFiles(:).dcdOnlyf],'r','LineWidth',2)
legend('All trials','Only decoded trials')
title('Decoder Online Performance','FontWeight','Bold')
xlabel('Session')
ylabel('Performance')
xTicks = 0:length(xLabelStr);
set(gca,'XTickLabel',xLabelStr,'XTick',xTicks)
