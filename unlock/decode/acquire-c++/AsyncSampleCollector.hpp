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

#ifndef ASYNC_SAMPLE_COLLECTOR_HPP
#define ASYNC_SAMPLE_COLLECTOR_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/atomic.hpp>
#include <cstddef>

#include "ISignal.hpp"
#include "Sample.hpp"
#include "SampleBuffer.hpp"
#include "IWorkController.hpp"
#include "Portability.hpp"

using namespace boost;
using namespace boost::lockfree;

class DllExport AsyncSampleCollector
{
 public:
  AsyncSampleCollector(ISignal* pSignal, lockfree::spsc_queue<Sample<uint32_t> >* pQueue,
		       IWorkController* pWorkController, Sample<uint32_t>* pSamples,
		       size_t samplesSize, SampleBuffer<uint32_t>* pRingBuffer);
  AsyncSampleCollector(const AsyncSampleCollector& copy);
  virtual ~AsyncSampleCollector();
  
 public:
  size_t currentSample() const;
  void  incrementCurrentSample();

 public:
  AsyncSampleCollector& operator=(const AsyncSampleCollector& rhs);
  bool operator==(const AsyncSampleCollector& rhs) const;
  bool operator!=(const AsyncSampleCollector& rhs) const;  
  void operator()();
  
 private:
  ISignal* mpSignal;
  spsc_queue<Sample<uint32_t> >* mpQueue;
  IWorkController* mpWorkController;
  Sample<uint32_t>* mpSamples;
  size_t mSamplesSize;
  size_t mCurrentSample;
  SampleBuffer<uint32_t>* mpRingBuffer;
};

#endif
