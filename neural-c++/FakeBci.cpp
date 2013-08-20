#include <boost/random/uniform_int_distribution.hpp>
#include <limits>

#include "fakeBci.hpp"

FakeBci::FakeBci()
  : mOpenCount(0), mOpenRet(true), mInitCount(0), mLastChannels(4), mInitRet(true), mChannelsCount(0), mStartCount(0), mStartRet(true),
    mAcquireCount(0), mAcquireRet(1), mGetDataCount(0), mpLastGetData(0), mLastSamples(0),
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

FakeBci::~FakeBci() {
}

bool FakeBci::open(uint8_t* pMacAddress) {
  BOOST_VERIFY(pMacAddress != 0);	
  mOpenCount++;
  std::copy(pMacAddress, pMacAddress+MAC_ADDRESS_SIZE, mLastMac);
  return mOpenRet;
}

bool FakeBci::init(size_t channels) {
  mInitCount++;
  mLastChannels = channels;
  return mInitRet;
}

size_t FakeBci::channels() {
  mChannelsCount++;
  return mLastChannels;
}

bool FakeBci::start() {
  mStartCount++;
  return mStartRet;
}

size_t FakeBci::acquire() {
  mAcquireCount++;
  return mAcquireRet;
}

void FakeBci::getdata(uint32_t* buffer, size_t samples) {
  BOOST_VERIFY(buffer != 0);
  BOOST_VERIFY(mAcquireRet == samples);
  mGetDataCount++;
  for(size_t i=0; i < samples; i++) {
    for (size_t j=0; j < mLastChannels; j++) {
      boost::random::uniform_int_distribution<> dist(1, std::numeric_limits<int32_t>::max());
      buffer[i+j] = (uint32_t)dist(gen);
    }
  }
  mpLastGetData = buffer;
  mLastSamples = samples;
}

uint64_t FakeBci::timestamp() {
  mTimestampCount++;
  return mTimestampRet;
}

bool FakeBci::stop() {
  mStopCount++;
  return mStopRet;
}

bool FakeBci::close() {
  mCloseCount++;
  return mCloseRet;
}

