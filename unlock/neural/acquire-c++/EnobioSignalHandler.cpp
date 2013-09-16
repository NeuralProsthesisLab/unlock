#include <stdio.h>
#include <iostream>
#include <boost/assert.hpp>
#include <climits>

#include "EnobioSignalHandler.hpp"

using namespace std;

static const size_t DATA_CHANNELS = 8;
static const size_t TIME_CHANNELS = 3;
static const size_t BUFFER_SAMPLES = 32768;
static const size_t CHANNELS = DATA_CHANNELS+TIME_CHANNELS;

EnobioSignalHandler::EnobioSignalHandler(Enobio3G* pEnobio3G) : mpEnobio3G(pEnobio3G), mpDataReceiver(0), mpStatusReceiver(0),
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

	for(size_t i=0; i < CHANNELS; i++) {
	  mRawEnobioLog << ((int32_t*)(mpRawBuffer+CHANNELS*mNumSamples))[i] << " ";
	}
	mRawEnobioLog << endl;

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
	BOOST_VERIFY(mpEnobio3G != 0);
    // hardcoded MAC of our Enobio 8 device
    // will not work with the StarStim. needs refactoring
    unsigned char hardcodedMac[6] = {0x61, 0x9C, 0x58, 0x80, 0x07, 0x00};
    int opened = mpEnobio3G->openDevice(hardcodedMac);
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
		cerr << "Pynobio: ERROR: waiting result = " << waitResult << endl;
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
		cout << "Enobio.getdata: WARNING: number of samples requested is bigger than the buffer" << endl;
		samples = BUFFER_SAMPLES*CHANNELS;
	}
	memcpy(buffer, mpSamples, samples*sizeof(uint32_t));
}

uint64_t EnobioSignalHandler::timestamp() {
    return mTimeStamp;
}

bool EnobioSignalHandler::stop() {
    mpEnobio3G->stopStreaming();
    mStarted = false;
    return true;
}

bool EnobioSignalHandler::close() {
    mpEnobio3G->closeDevice();
    mOpened = false;
    return true;
}
