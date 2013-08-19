function [ADJUSTEDvector] = mvgAverage(RAWvector, sampleSize)
% This function takes as its input a vector and sample size
% and outputs a vector passed through a moving average.  The output vector
% has a length of the input vector length minus the sample size plus one.
% form: [ADJUSTEDvector}=mvgAverage(RAWvector,sampleSize)

    RAWmat = zeros(sampleSize, length(RAWvector));
    [r c] = size(RAWvector);
    if r>1
        RAWvector=RAWvector';
    end
    
    for i = 2:sampleSize
        RAWmat(i,:) = circshift(RAWvector, [0 (1-i)]);
    end

    RAWmat(1,:)=RAWvector;
    RAWmat=RAWmat(:,1:(length(RAWvector)-sampleSize+1));
    temp=mean(RAWmat);

    ADJUSTEDvector=temp;

end