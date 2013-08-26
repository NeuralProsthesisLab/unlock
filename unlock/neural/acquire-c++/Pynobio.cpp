#include "Pynobio.hpp"
#include <stdio.h>

//// EnobioDataConsumer ///
EnobioDataConsumer::EnobioDataConsumer() {
	this->buffer = new int[BUFFER_SAMPLES*CHANNELS];
	this->nSamples = 0;
	this->hEvent = CreateEvent(NULL, false, false, NULL);
	if(this->hEvent == NULL) {
		printf("CreateEvent failed (%d)\n", GetLastError());
	}
}

EnobioDataConsumer::~EnobioDataConsumer() {
	CloseHandle(this->hEvent);
	delete this->buffer;
}

void EnobioDataConsumer::receiveData(const PData &data) {
	// we cannot ensure consistent polling, so we need to add
	// a buffer and a sample counter in order to inform python
	// how many samples we need to retrieve at a time.
	// a first pass will be that acquire does a buffer copy
	// based on the sample count, which then resets it.
	// if race collisions occur and are problematic, we could 
	// try double buffering
	ChannelData *pData = (ChannelData *)data.getData();
	int *sample = pData->data();
	memcpy(this->buffer + CHANNELS*this->nSamples, sample, CHANNELS*sizeof(int));
	//for(int i=0; i < 8; i++) {
	//	this->buffer[nSamples*8+i] = pData->data()[i];
	//}
	this->timestamp = pData->timestamp();
	this->nSamples++;
	if(this->nSamples >= BUFFER_SAMPLES) {
		this->nSamples = 0;
	}
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
Enobio::Enobio() {

	this->enobioData = new EnobioDataConsumer();
	this->enobioStatus = new EnobioStatusConsumer();
	this->enobio.registerConsumer(Enobio3G::ENOBIO_DATA, *this->enobioData);
	this->enobio.registerConsumer(Enobio3G::STATUS, *this->enobioStatus);

	this->opened = false;
	this->started = false;
	this->samples = new size_t[BUFFER_SAMPLES*CHANNELS];
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
//	this->opened = (uint32_t)this->enobio.openDevice(hardcodedMac);
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
//	this->enobio.startStreaming();
	this->started = true;
	return this->started;
}

size_t Enobio::acquire() {
	size_t result=0;
	result = WaitForSingleObject(this->enobioData->hEvent, 1000);
	if (result != WAIT_OBJECT_0) {
		printf("Wait error (%d)\n",result);
		return 0;
	} else {
		int nSamples = this->enobioData->nSamples;
		memcpy(this->samples, this->enobioData->buffer, CHANNELS*nSamples*sizeof(int));
		this->enobioData->nSamples = 0;
		return nSamples;
	}	
}

void Enobio::getdata(uint32_t* buffer, size_t samples) {
	if(samples >= BUFFER_SAMPLES*CHANNELS) {
		samples = BUFFER_SAMPLES*CHANNELS;
	}
	memcpy(buffer, this->samples, samples*sizeof(size_t));
}

uint64_t Enobio::timestamp() {
	return this->enobioData->timestamp;
}

bool Enobio::stop() {
//	this->enobio.stopStreaming();
	this->started = false;
	return true;
}

bool Enobio::close() {
//	this->enobio.closeDevice();
	this->opened = false;
	return true;
}
