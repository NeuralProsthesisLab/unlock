#include <boost/random/uniform_int_distribution.hpp>
#include <limits>
#include <iostream>

#include "fakeBci.hpp"

using namespace std;

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

bool FakeBci::open(uint8_t mac[]) {
	BOOST_VERIFY(sizeof(mac) >= MAC_ADDRESS_SIZE);
	mOpenCount++;
	std::copy(mac, mac+MAC_ADDRESS_SIZE, mLastMac);
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
	cout << "Acquire  " << mAcquireRet << endl;	
	mAcquireCount++;
	return mAcquireRet;
}

void FakeBci::getdata(uint32_t* buffer, size_t samples) {
	cout << "BUffer " << buffer << ":" << samples << endl;
	BOOST_VERIFY(buffer != 0);
	BOOST_VERIFY(mAcquireRet == samples);
	mGetDataCount++;
	for(int i=0; i < samples; i++) {
		for (int j=0; j < channels; j++) {
			boost::random::uniform_int_distribution<> dist(0, std::numeric_limits<uint32_t>::max());
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

