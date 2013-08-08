#include "fake_bci.hpp"
#include <limits>
#include <boost/random/uniform_int_distribution.hpp>

FakeBCI::FakeBCI()
	: mOpenCount(0), mOpenRet(true), mInitCount(0), mLastChannels(0), mInitRet(true), mStartCount(0), mStartRet(true),
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

FakeBCI::~FakeBCI() {
}

#include <iostream>
using namespace std;

bool FakeBCI::open(uint8_t mac[]) {
	BOOST_VERIFY(sizeof(mac) >= MAC_ADDRESS_SIZE);
	mOpenCount++;
	std::copy(mac, mac+MAC_ADDRESS_SIZE, mLastMac);
	return mOpenRet;
}

bool FakeBCI::init(size_t channels) {
	mInitCount++;
	mLastChannels = channels;
	return mInitRet;
}

bool FakeBCI::start() {
	mStartCount++;
	return mStartRet;
}

size_t FakeBCI::acquire() {
	mAcquireCount++;
	return mAcquireRet;
}

void FakeBCI::getdata(uint32_t* buffer, size_t samples) {
	BOOST_VERIFY(buffer != 0);
	BOOST_VERIFY(mAcquireRet == samples);
	mGetDataCount++;
	for(int i=0; i < samples; i++) {
		boost::random::uniform_int_distribution<> dist(0, std::numeric_limits<uint32_t>::max());
		buffer[i] = (uint32_t)dist(gen);
	}
	mpLastGetData = buffer;
	mLastSamples = samples;
}

uint64_t FakeBCI::timestamp() {
	mTimestampCount++;
	return mTimestampRet;
}

bool FakeBCI::stop() {
	mStopCount++;
	return mStopRet;
}

bool FakeBCI::close() {
	mCloseCount++;
	return mCloseRet;
}

