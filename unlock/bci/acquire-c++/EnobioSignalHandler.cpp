
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

#include <stdio.h>
#include <iostream>
#include <boost/assert.hpp>
#include <climits>

#include "EnobioSignalHandler.hpp"

using namespace std;

static const size_t DATA_CHANNELS = 8;
static const size_t TIME_CHANNELS = 5;
static const size_t BUFFER_SAMPLES = 32768;
static const size_t CHANNELS = DATA_CHANNELS+TIME_CHANNELS;

EnobioSignalHandler::EnobioSignalHandler(Enobio3G* pEnobio3G, ITimer* pTimer) : mpEnobio3G(pEnobio3G), mpTimer(pTimer), mpDataReceiver(0), mpStatusReceiver(0),
	mpRawBuffer(0), mpSamples(0), mNumSamples(0), mNumChannels(CHANNELS), mTimeStamp(0), mhEvent(0),
	mMutex(), mOpened(false), mStarted(false) {
	mhEvent = CreateEvent(0, false, false, 0);
	if(mhEvent == 0) {
		printf("CreateEvent failed (%d)\n", GetLastError());
	}

	//this->enobioData = new EnobioDataConsumer(&mMutex);
	//this->enobioStatus =  EnobioStatusConsumer();
//      this->enobio.registerConsumer(Enobio3G::ENOBIO_DATA, *this->enobioData);
//      this->enobio.registerConsumer(Enobio3G::STATUS, *this->enobioStatus);

	mpSamples = new uint32_t[BUFFER_SAMPLES*CHANNELS];
	mpRawBuffer = new uint32_t[BUFFER_SAMPLES*CHANNELS];
	BOOST_VERIFY(mpSamples != 0 && mpRawBuffer != 0 && mpEnobio3G != 0);
	mRawEnobioLog.open("raw-enobio-signal.log");
}

EnobioSignalHandler::~EnobioSignalHandler() {
	if(mStarted) {
		stop();
	}
	
	if(mOpened) {
		close();
	}

	CloseHandle(mhEvent);
	
	if(mpRawBuffer != 0) {
		delete mpRawBuffer;
		mpRawBuffer = 0;
	}
	
	if(mpSamples != 0) {
		delete mpSamples;
		mpSamples = 0;
    }
	
	if(mpDataReceiver != 0) {
		delete mpDataReceiver;
		mpDataReceiver = 0;
	}
	
	if(mpStatusReceiver != 0) {
		delete mpStatusReceiver;
		mpStatusReceiver = 0;
	}
#if 0
	if(mpTimer != 0) {
		delete mpTimer;
		mpTimer = 0;
	}
#endif

	if(mpEnobio3G != 0) {
		delete mpEnobio3G;
		mpEnobio3G = 0;
	}
}

void EnobioSignalHandler::setEnobioDataReceiver(EnobioDataReceiver* pDataReceiver) {
	BOOST_VERIFY(pDataReceiver != 0);
	mpDataReceiver = pDataReceiver;
	mpDataReceiver->registerConsumer(mpEnobio3G);
}

void EnobioSignalHandler::setEnobioStatusReceiver(EnobioStatusReceiver* pStatusReceiver) {
	BOOST_VERIFY(pStatusReceiver != 0);
	mpStatusReceiver = pStatusReceiver;
	mpStatusReceiver->registerConsumer(mpEnobio3G);	
}

void EnobioSignalHandler::handleStatusData(StatusData* pStatusData) {
	if(pStatusData != 0) {
		printf("%s\n", pStatusData->getString());
	} else {
		printf("STATUS DATA NULL");
	}
}

void EnobioSignalHandler::handleChannelData(ChannelData* pChannelData) {
	BOOST_VERIFY(mpRawBuffer != 0);
	BOOST_VERIFY(mNumSamples < BUFFER_SAMPLES);

	if (pChannelData == 0) {
		cerr << "EnobioSignalHandler.receiveData: WARNING pData == 0 " << endl;
		return;
	}
	uint32_t *sample = reinterpret_cast<uint32_t*>(pChannelData->data());
	if(sample == 0) {
		cerr << "EnobioSignalHandler.receiveData: WARNING samples == 0 " << endl;               
		return;
	}
	
	mMutex.lock();
	size_t offset = CHANNELS*mNumSamples;
	memcpy(mpRawBuffer+offset, sample, DATA_CHANNELS*sizeof(uint32_t));
	offset += DATA_CHANNELS;
	
	uint64_t sampleTimeStamp = pChannelData->timestamp();
	if(sampleTimeStamp < mTimeStamp) {
		cerr << "EnobioSignalHandler.handleChannelData: WARNING timestamps are decreasing " << endl;
		sampleTimeStamp = mTimeStamp;
	}
	
	uint64_t delta = sampleTimeStamp - mTimeStamp;
	if(delta > (uint64_t)UINT_MAX) {
		cerr << "EnobioSignalHandler.handleChannelData: WARNING delta = " << delta
			 << ", which cannot be stored in a signed 32 bit integer; value will be truncated " << endl;
	}
	mTimeStamp = sampleTimeStamp;
	uint32_t low32 = (uint32_t)mTimeStamp;
    uint32_t high32 = (uint32_t)(mTimeStamp >> 32);
	
	*(mpRawBuffer+offset) = (uint32_t)delta;
	offset++;
	*(mpRawBuffer+offset) = (uint32_t)high32;
	offset++;
	*(mpRawBuffer+offset) = (uint32_t)low32;
	offset++;
	*(mpRawBuffer+offset) = mpTimer->elapsedMicroSecs();
	offset++;
	*(mpRawBuffer+offset) = (uint32_t)0;

#if RAW_ENOBIO_LOG
	for(size_t i=0; i < CHANNELS; i++) {
	  mRawEnobioLog << ((int32_t*)(mpRawBuffer+CHANNELS*mNumSamples))[i] << " ";
	}
	mRawEnobioLog << endl;
#endif

	mNumSamples++;
	if(mNumSamples == BUFFER_SAMPLES) {
		mNumSamples = 0;
	}
	mMutex.unlock();
	if(!SetEvent(mhEvent)) {
		printf("SetEvent failed (%d)\n", GetLastError());
	}       
}

bool EnobioSignalHandler::open(uint8_t* mac) {
	BOOST_VERIFY(mpEnobio3G != 0 && mac != 0);
    int opened = mpEnobio3G->openDevice(mac);
    if(opened == 0) {
        mOpened = false;
    } else {
        mOpened = true;
    }
    return mOpened;
}

bool EnobioSignalHandler::init(size_t channels) {
    // it does not appear as if the Enobio has a way to only request a
    // subset of channels, so we would use this to create a mask on the
    // returned sample data.
    return true;
}

size_t EnobioSignalHandler::channels() {
    // XXX - fix me
    return CHANNELS;
}

bool EnobioSignalHandler::start() {
	BOOST_VERIFY(mpEnobio3G != 0);	
    mpEnobio3G->startStreaming();
    mStarted = true;
    return mStarted;
}

size_t EnobioSignalHandler::acquire() {
	BOOST_VERIFY(mpRawBuffer != 0 && mpSamples != 0);
	size_t waitResult = WaitForSingleObject(mhEvent, 1000);
	if (waitResult != WAIT_OBJECT_0) {
		cerr << "EnobioSignalHandler: ERROR: waiting result = " << waitResult << endl;
		return 0;
	} else {
		mMutex.lock();
		memcpy(mpSamples, mpRawBuffer, CHANNELS*mNumSamples*sizeof(uint32_t));
		size_t ret = mNumSamples*CHANNELS;
		mNumSamples = 0;
		mMutex.unlock();
		return ret;
	}       
}

void EnobioSignalHandler::getdata(uint32_t* buffer, size_t samples) {
	BOOST_VERIFY(buffer != 0 && mpSamples != 0);
	if(samples > BUFFER_SAMPLES*CHANNELS) {
		cout << "EnobioSignalHandler.getdata: WARNING: number of samples requested is bigger than the buffer" << endl;
		samples = BUFFER_SAMPLES*CHANNELS;
	}
	memcpy(buffer, mpSamples, samples*sizeof(uint32_t));
}

uint64_t EnobioSignalHandler::timestamp() {
    return mTimeStamp;
}

bool EnobioSignalHandler::stop() {
	cout << "Stop streaming called" << endl;
    mpEnobio3G->stopStreaming();
    mStarted = false;
    return true;
}

bool EnobioSignalHandler::close() {
	cout << " Close called " << endl;
    mpEnobio3G->closeDevice();
    mOpened = false;
    return true;
}
