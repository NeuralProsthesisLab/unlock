
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

#include <boost/assert.hpp>
#include <boost/thread.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"

using namespace boost;
using namespace std;

AsyncSampleCollector::AsyncSampleCollector(ISignal* pSignal,
					   lockfree::spsc_queue<Sample<uint32_t> >* pQueue,
					   IWorkController* pWorkController, Sample<uint32_t>* pSamples, size_t samplesSize, SampleBuffer<uint32_t>* pRingBuffer) 
  : mpSignal(pSignal), mpQueue(pQueue), mpWorkController(pWorkController), mpSamples(pSamples), mSamplesSize(samplesSize),
    mpRingBuffer(pRingBuffer), mCurrentSample(0)
{
  BOOST_VERIFY(mpSignal != 0);
  BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
  BOOST_VERIFY(mpWorkController != 0);
  BOOST_VERIFY(mpSamples != 0);
  BOOST_VERIFY(mSamplesSize > 0);
  BOOST_VERIFY(mpRingBuffer != 0);
}

AsyncSampleCollector::AsyncSampleCollector(const AsyncSampleCollector& copy)
  : mpSignal(copy.mpSignal), mpQueue(copy.mpQueue), mpWorkController(copy.mpWorkController), mpSamples(copy.mpSamples),
    mSamplesSize(copy.mSamplesSize), mCurrentSample(copy.mCurrentSample), mpRingBuffer(copy.mpRingBuffer){
}
    
    
AsyncSampleCollector::~AsyncSampleCollector() {
  mpSamples=0;
  mpRingBuffer=0;
  mpSignal=0;
  mpWorkController=0;
  mpQueue=0;
    
} 

size_t AsyncSampleCollector::currentSample() const {
  return mCurrentSample;
}

void  AsyncSampleCollector::incrementCurrentSample() {
  BOOST_VERIFY(mCurrentSample < mSamplesSize);
  mCurrentSample++;
  if (mCurrentSample == mSamplesSize) {
    mCurrentSample = 0;
  }
}  

AsyncSampleCollector& AsyncSampleCollector::operator=(const AsyncSampleCollector& rhs) {
  mpSignal = rhs.mpSignal;
  mpQueue = rhs.mpQueue;
  mpWorkController = rhs.mpWorkController;
  mpSamples = rhs.mpSamples;
  mSamplesSize = rhs.mSamplesSize;
  mCurrentSample = rhs.mCurrentSample;
  mpRingBuffer = rhs.mpRingBuffer;
  return *this;
}
  
bool AsyncSampleCollector::operator==(const AsyncSampleCollector& rhs) const {
  if (mpSignal == rhs.mpSignal && mpQueue == rhs.mpQueue && mpWorkController == rhs.mpWorkController
      && mpSamples == rhs.mpSamples && mpRingBuffer == rhs.mpRingBuffer
      && mCurrentSample == rhs.mCurrentSample) {
    return true;
  } else {
    return false;
  }
}
  
bool AsyncSampleCollector::operator!=(const AsyncSampleCollector& rhs) const {
  return !(*this == rhs);
}
  
void AsyncSampleCollector::operator()() {
  BOOST_VERIFY(mpSignal != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0 && mpWorkController != 0);
  size_t iterations = 0;
  while(mpWorkController->doWork()) {
    try {
    BOOST_VERIFY(mpSignal != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0 && mpWorkController != 0);      
    
    size_t samples = mpSignal->acquire();
    if (samples > 0) {
      if (samples > mpRingBuffer->maximumReservation()) {
        cerr << "AsyncSampleCollector.operator()(): WARNING: samples acquire == " << samples << ", but the ring size == " << mpRingBuffer->maximumReservation() << " dropping extra requests " << endl;
        samples = mpRingBuffer->maximumReservation();
      }
      
      uint32_t* pBuffer = mpRingBuffer->reserve(samples);
      if (pBuffer == 0) {
	cerr << "AsyncSampleCollector.operator()(): ERROR: mpRingBuffer failed to reserve buffer; dropping these samples " << endl;
	continue;
      }
      
      mpSignal->getdata(pBuffer, samples);
      BOOST_VERIFY(mCurrentSample < mSamplesSize);
      mpSamples[mCurrentSample].configure(pBuffer, samples);
      
      while (!mpQueue->push(mpSamples[mCurrentSample])) {
        if (!mpWorkController->doWork()) {
	  cerr << "AsyncSampleCollector.operator()(): WARNING stopping work with a full queue" << endl;
	  break;
        }
      }
      incrementCurrentSample();
    }
    boost::this_thread::sleep(boost::posix_time::microseconds(100));
    } catch(...) {
      cerr << "AsyncSampleCollector.operator()(): ERROR unhandled exception; ignoring " << endl;
    }
  }
}
   
