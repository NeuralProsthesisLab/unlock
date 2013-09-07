#include <stdio.h>
#include <iostream>
#include <boost/assert.hpp>

#include "Pynobio.hpp"

using namespace std;

//// EnobioDataConsumer ///
EnobioDataConsumer::EnobioDataConsumer(boost::mutex* pMutex) :mpMutex(pMutex) {
	BOOST_VERIFY(mpMutex != 0);
	this->buffer = new uint32_t[BUFFER_SAMPLES*CHANNELS];
	this->nSamples = 0;
	this->hEvent = CreateEvent(NULL, false, false, NULL);
	if(this->hEvent == 0) {
		printf("CreateEvent failed (%d)\n", GetLastError());
	}
}

EnobioDataConsumer::~EnobioDataConsumer() {
	CloseHandle(this->hEvent);
	BOOST_VERIFY(this->buffer != 0);
	delete this->buffer;
}

void EnobioDataConsumer::receiveData(const PData &data) {
	BOOST_VERIFY(mpMutex != 0 && buffer != 0);
	BOOST_VERIFY(this->nSamples < BUFFER_SAMPLES);
	ChannelData *pData = (ChannelData *)data.getData();
	if (pData == 0) {
		cerr << "EnobioDataConsumer.receiveData: WARNING pData ==0 " << endl;
		return;
	}
	uint32_t *sample = reinterpret_cast<uint32_t*>(pData->data());
	if(sample == 0) {
		cerr << "EnobioDataConsumer.receiveData: WARNING samples ==0 " << endl;		
		return;
	}
	
	mpMutex->lock();
	memcpy(this->buffer + CHANNELS*this->nSamples, sample, CHANNELS*sizeof(uint32_t));
	this->timestamp = pData->timestamp();
	this->nSamples++;
	if(this->nSamples == BUFFER_SAMPLES) {
		this->nSamples = 0;
	}
	mpMutex->unlock();
	if(!SetEvent(this->hEvent)) {
		printf("SetEvent failed (%d)\n", GetLastError());
	}
}


//// EnobioStatusConsumer ///
void EnobioStatusConsumer::receiveData(const PData &data) {
	StatusData *status = (StatusData *)data.getData();
	printf("%s\n", status->getString());
}


/// Enobio ///
Enobio::Enobio() :mutex() {

	this->enobioData = new EnobioDataConsumer(&mutex);
	this->enobioStatus = new EnobioStatusConsumer();
	this->enobio.registerConsumer(Enobio3G::ENOBIO_DATA, *this->enobioData);
	this->enobio.registerConsumer(Enobio3G::STATUS, *this->enobioStatus);

	this->opened = false;
	this->started = false;
	this->samples = new uint32_t[BUFFER_SAMPLES*CHANNELS];
}

Enobio::~Enobio() {
	if(this->started) {
		this->stop();
	}
	if(this->opened) {
		this->close();
	}

	delete this->enobioStatus;
	delete this->enobioData;
	delete this->samples;
}

bool Enobio::open(uint8_t* mac) {
	// hardcoded MAC of our Enobio 8 device
	// will not work with the StarStim. needs refactoring
	unsigned char hardcodedMac[6] = {0x61, 0x9C, 0x58, 0x80, 0x07, 0x00};
	this->opened = (uint32_t)this->enobio.openDevice(hardcodedMac);
	return this->opened;
}

bool Enobio::init(size_t channels) {
	// it does not appear as if the Enobio has a way to only request a
	// subset of channels, so we would use this to create a mask on the
	// returned sample data.
	return true;
}

size_t Enobio::channels() {
	// XXX - fix me
	return 8;
}

bool Enobio::start() {
	this->enobio.startStreaming();
	this->started = true;
	return this->started;
}

size_t Enobio::acquire() {
	BOOST_VERIFY(this->enobioData != 0 && this->enobioData->buffer != 0 && this->samples != 0);
	size_t result=0;
	result = WaitForSingleObject(this->enobioData->hEvent, 1000);
	if (result != WAIT_OBJECT_0) {
		cerr << "Pynobio: ERROR: waiting result = " << result << endl;
		return 0;
	} else {
		mutex.lock();
		int nSamples = this->enobioData->nSamples;
		memcpy(this->samples, this->enobioData->buffer, CHANNELS*nSamples*sizeof(uint32_t));
		this->enobioData->nSamples = 0;
		mutex.unlock();
		return nSamples*CHANNELS;
	}	
}

void Enobio::getdata(uint32_t* buffer, size_t samples) {
	BOOST_VERIFY(buffer != 0 && this->samples != 0);	
	if(samples > BUFFER_SAMPLES*CHANNELS) {
		cout << "Enobio.getdata: WARNING: number of samples requested is bigger than the buffer" << endl;
		samples = BUFFER_SAMPLES*CHANNELS;
	}
	memcpy(buffer, this->samples, samples*sizeof(uint32_t));
}

uint64_t Enobio::timestamp() {
	return this->enobioData->timestamp;
}

bool Enobio::stop() {
	this->enobio.stopStreaming();
	this->started = false;
	return true;
}

bool Enobio::close() {
	this->enobio.closeDevice();
	this->opened = false;
	return true;
}
