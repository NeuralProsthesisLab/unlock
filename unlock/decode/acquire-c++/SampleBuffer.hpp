#ifndef SAMPLE_BUFFER_HPP
#define SAMPLE_BUFFER_HPP

#include <boost/assert.hpp>
#include "Portability.hpp"

template<class T>
class DllExport SampleBuffer
{
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
    return RING_SIZE;
  }
    
  T* reserve(size_t samples) {
    BOOST_VERIFY(mpBuffer != 0);
        
    if (samples > maximumReservation()) {
      cerr << "SampleBuffer.reserve: ERROR: a reservation larger than the maximum reservation; returning 0 " << endl;
      return 0;
    }
        
    if ((mPosition + samples) >= maximumReservation()) {
      mPosition = 0;
    }
        
    T* ret = mpBuffer+mPosition;
    mPosition += samples;
    return ret;
  }
    
 private:
  static const size_t RING_SIZE=1048576;
  T* mpBuffer;
  size_t mPosition;
};

#endif
