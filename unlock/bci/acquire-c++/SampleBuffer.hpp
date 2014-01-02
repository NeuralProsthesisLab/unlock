
// Copyright (c) James Percent and Unlock contributors.
// All rights reserved.
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//    1. Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//    
//    2. Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//    3. Neither the name of Unlock nor the names of its contributors may be used
//       to endorse or promote products derived from this software without
//       specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
// ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
// ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
