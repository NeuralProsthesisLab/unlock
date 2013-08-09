#ifndef SAMPLE_BUFFER_HPP
#define SAMPLE_BUFFER_HPP

#include <boost/assert.hpp>

template<class T>
class SampleBuffer {
public:
    static const size_t RING_SIZE=1048576;
    
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

  size_t maximumReservation() {
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
