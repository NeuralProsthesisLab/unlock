
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

#ifndef NONBLOCKING_SIGNAL_HPP
#define NONBLOCKING_SIGNAL_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/thread.hpp>
#include <boost/atomic.hpp>

#include "ISignal.hpp"
#include "Sample.hpp"
#include "SampleBuffer.hpp"
#include "ManagedWorkController.hpp"
#include "Portability.hpp"

class DllExport NonblockingSignal : public ISignal
{
 public: 
  static const size_t SAMPLE_BUFFER_SIZE=16384;
    
 public:
  NonblockingSignal(ISignal* pSignal);
  NonblockingSignal(const NonblockingSignal& copy);
  virtual ~NonblockingSignal();
  NonblockingSignal& operator=(const NonblockingSignal& other);
  
 public:
  virtual bool open(uint8_t*);
  virtual bool init(size_t);
  virtual size_t channels();
  virtual bool start();
  virtual size_t acquire();
  virtual void getdata(uint32_t* data, size_t n);
  virtual uint64_t timestamp();
  virtual bool stop();
  virtual bool close();

 private:
  void waitForAsyncCollector();
  
 private:
  ISignal* mpSignal;
  Sample<uint32_t>* mpProducerSamples;
  Sample<uint32_t>* mpConsumerSamples;
  SampleBuffer<uint32_t>* mpSampleRingBuffer;
  boost::lockfree::spsc_queue<Sample<uint32_t> >* mpQueue;
  boost::thread* mpAsyncSampleCollector;
  ManagedWorkController* mpWorkController;
};

#endif
