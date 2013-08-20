#ifndef SAMPLE_HPP
#define SAMPLE_HPP

#include <cstddef>
#include "Portability.hpp"

template<class T>
class DllExport Sample
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
    return (T*)mpSample;
  }
    
  size_t length() {
    return (size_t)mLength;
  }
    
 private:   
  volatile T* mpSample;
  volatile size_t mLength;
};

#endif
