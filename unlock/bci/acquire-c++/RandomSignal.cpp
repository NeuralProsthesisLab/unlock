
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

#include <boost/random/uniform_int_distribution.hpp>
#include <limits>

#include "RandomSignal.hpp"

RandomSignal::RandomSignal()
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

RandomSignal::~RandomSignal() {
}

bool RandomSignal::open(uint8_t* pMacAddress) {
  BOOST_VERIFY(pMacAddress != 0);	
  mOpenCount++;
  std::copy(pMacAddress, pMacAddress+MAC_ADDRESS_SIZE, mLastMac);
  return mOpenRet;
}

bool RandomSignal::init(size_t channels) {
  mInitCount++;
  mLastChannels = channels;
  return mInitRet;
}

size_t RandomSignal::channels() {
  mChannelsCount++;
  return mLastChannels;
}

bool RandomSignal::start() {
  mStartCount++;
  return mStartRet;
}

size_t RandomSignal::acquire() {
  mAcquireCount++;
  return mAcquireRet;
}

void RandomSignal::getdata(uint32_t* buffer, size_t samples) {
  BOOST_VERIFY(buffer != 0);
  mGetDataCount++;
  for(size_t i=0; i < samples; i++) {
    boost::random::uniform_int_distribution<> dist(1, std::numeric_limits<int32_t>::max());
    buffer[i] = (uint32_t)dist(gen);
  }
  buffer[samples - 1] = 0;
  mpLastGetData = buffer;
  mLastSamples = samples;
}

uint64_t RandomSignal::timestamp() {
  mTimestampCount++;
  return mTimestampRet;
}

bool RandomSignal::stop() {
  mStopCount++;
  return mStopRet;
}

bool RandomSignal::close() {
  mCloseCount++;
  return mCloseRet;
}

