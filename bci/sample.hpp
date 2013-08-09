#ifndef SAMPLE_HPP
#define SAMPLE_HPP

#include <cstddef>

template<class T>
class Sample
{
public:
    Sample() : mpSample(0), mLength(0) {}
    
    Sample(const Sample &copy) : mpSample(copy.mpSample), mLength(copy.mLength) {
    }
    
    ~Sample() {
        mpSample = 0;
        mLength = 0;
    }
    
    Sample& operator=(const Sample& other) {
        mpSample = other.mpSample;
        mLength = other.mLength;
        return *this;
    }
    
    void configure(T* pSample, int length) {
        mpSample = pSample;
        mLength = length;        
    }
 
    T* sample() {
        return mpSample;
    }
    
    size_t length() {
        return mLength;
    }
    
private:   
    T* mpSample;
    size_t mLength;
};

#endif