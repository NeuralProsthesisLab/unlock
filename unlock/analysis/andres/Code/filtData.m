function [unlockFiltData,unlockInfo] = filtData(unlockData,unlockInfo)
%
%
%
%
%
% Andres. v.1. 02 Jan 2014.

%% Filter params
smpRate     = unlockInfo.main.Fs;
freqBand    = unlockInfo.main.freqBand;
filterOrder = unlockInfo.main.filterOrder; 
filterType  = unlockInfo.main.filterType;
[filtParams]= setFilterParams(freqBand, filterType, filterOrder, smpRate);

%% Filtering
if ~unlockInfo.main.doFilterData
    unlockFiltData = filtfilt(filtParams.b,filtParams.a,unlockData.data);
    unlockInfo.main.dataFiltered = true;            % setting flag for filtered data
else
    fprintf('Data already filtered!!\n')
    unlockFiltData = unlockData;
end


