#include <boost/random/uniform_int_distribution.hpp>
#include <limits>

#include "fakeSignal.hpp"

FakeSignal::FakeSignal()
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

FakeSignal::~FakeSignal() {
}

bool FakeSignal::open(uint8_t* pMacAddress) {
  BOOST_VERIFY(pMacAddress != 0);	
  mOpenCount++;
  std::copy(pMacAddress, pMacAddress+MAC_ADDRESS_SIZE, mLastMac);
  return mOpenRet;
}

bool FakeSignal::init(size_t channels) {
  mInitCount++;
  mLastChannels = channels;
  return mInitRet;
}

size_t FakeSignal::channels() {
  mChannelsCount++;
  return mLastChannels;
}

bool FakeSignal::start() {
  mStartCount++;
  return mStartRet;
}

size_t FakeSignal::acquire() {
  mAcquireCount++;
  return mAcquireRet;
}

void FakeSignal::getdata(uint32_t* buffer, size_t samples) {
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

uint64_t FakeSignal::timestamp() {
  mTimestampCount++;
  return mTimestampRet;
}

bool FakeSignal::stop() {
  mStopCount++;
  return mStopRet;
}

bool FakeSignal::close() {
  mCloseCount++;
  return mCloseRet;
}

