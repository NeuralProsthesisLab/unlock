#include <boost/random/uniform_int_distribution.hpp>
#include <limits>

#include "RandomSignal.hpp"

RandomSignal::RandomSignal()
  : mOpenCount(0), mOpenRet(true), mInitCount(0), mLastChannels(4), mInitRet(true), mChannelsCount(0), mStartCount(0), mStartRet(true),
    mAcquireCount(0), mAcquireRet(4), mGetDataCount(0), mpLastGetData(0), mLastSamples(0),
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

