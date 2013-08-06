#ifndef RING_BUFFER_HPP
#define RING_BUFFER_HPP

#include <boost/assert.hpp>

static const size_t RING_SIZE=1048576;

template<class T>
class Sample {
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
    int mLength;
};

template<class T>
class SampleBuffer {
public:
    SampleBuffer() : mpBuffer(0), mPosition(0) {
        mpBuffer = new T[RING_SIZE];
    }
    
    SampleBuffer(const SampleBuffer& copy) :mpBuffer(copy.mpBuffer), mPosition(copy.mPosition) {
    }
    
    SampleBuffer& operator=(const SampleBuffer& other) {
        mpBuffer = other.mpBuffer;
        mPosition = other.mPosition;
    }
    
    ~SampleBuffer() {
        BOOST_VERIFY(mpBuffer != 0);
        delete[] mpBuffer;
    }

    size_t maximum_reservation() {
        return RING_SIZE-1;
    }
    
    T* reserve(size_t samples) {
        BOOST_VERIFY(mpBuffer != 0 && samples < RING_SIZE);
        
        if (samples >= RING_SIZE) {
            return 0;
        }
        
        if ((mPosition + samples) > RING_SIZE) {
            mPosition = 0;
        }
        
        T* ret = mpBuffer+mPosition;
        mPosition += samples;
        return ret;
    }
    
private:
    T* mpBuffer;
    size_t mPosition;
};

#endif