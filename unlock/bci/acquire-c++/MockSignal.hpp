
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

#ifndef MOCK_SIGNAL_HPP
#define MOCK_SIGNAL_HPP

#include "ISignal.hpp"
#include "Portability.hpp"

class DllExport MockSignal : public ISignal
{
 public:
  MockSignal()
  : mOpenCount(0), mOpenRet(true), mInitCount(0), mLastChannels(5), mInitRet(true), mChannelsCount(0), mStartCount(0), mStartRet(true),
    mAcquireCount(0), mAcquireRet(5), mGetDataCount(0), mpLastGetData(0), mLastSamples(0),
    mTimestampCount(0), mTimestampRet(-1), mStopCount(0), mStopRet(true), mCloseCount(0),
    mCloseRet(true)
{
  mLastMac[0] = 0xd;
  mLastMac[1] = 0xe;
  mLastMac[2] = 0xa;
  mLastMac[3] = 0xd;
  mLastMac[4] = 0xe;
  mLastMac[5] = 0xd;
}

  virtual ~MockSignal()  {}
  virtual bool open(uint8_t* mac) {
  BOOST_VERIFY(pMacAddress != 0);
  mOpenCount++;
  std::copy(pMacAddress, pMacAddress+MAC_ADDRESS_SIZE, mLastMac);
  return mOpenRet;
}

  virtual bool init(size_t channels) {
  mInitCount++;
  mLastChannels = channels;
  return mInitRet;
}

  virtual size_t channels() {
  mChannelsCount++;
  return mLastChannels;
}

  virtual bool start() {
  mStartCount++;
  return mStartRet;
}

  virtual size_t acquire(){
  mAcquireCount++;
  return mAcquireRet;
}


  virtual void getdata(uint32_t* buffer, size_t samples) {
  BOOST_VERIFY(buffer != 0);
  mGetDataCount++;
  for(size_t i=0; i < samples; i++) {
    buffer[i] = (uint32_t)i;
  }
  buffer[samples - 1] = 0;
  mpLastGetData = buffer;
  mLastSamples = samples;
}



  virtual uint64_t timestamp() {
  mTimestampCount++;
  return mTimestampRet;
}

  virtual bool stop()  {
  mStopCount++;
  return mStopRet;
}

  virtual bool close(){
  mCloseCount++;
  return mCloseRet;
}

 public:
  size_t mOpenCount;
  bool mOpenRet;
  uint8_t mLastMac[MAC_ADDRESS_SIZE];
  size_t mInitCount;
  size_t mLastChannels;
  bool mInitRet;
  size_t mChannelsCount;
  size_t mStartCount;
  bool mStartRet;
  size_t mAcquireCount;
  size_t mAcquireRet;
  size_t mGetDataCount;
  uint32_t* mpLastGetData;
  size_t mLastSamples;
  size_t mTimestampCount;
  uint64_t mTimestampRet;
  size_t mStopCount;
  bool mStopRet;
  size_t mCloseCount;
  bool mCloseRet;	
};

#endif
