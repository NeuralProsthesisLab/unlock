#include "pynobio.h"


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
	this->samples = new int[BUFFER_SAMPLES*CHANNELS];
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

BOOL Enobio::open() {
	// hardcoded MAC of our Enobio 8 device
	// will not work with the StarStim. needs refactoring
	unsigned char mac[6] = {0x61, 0x9C, 0x58, 0x80, 0x07, 0x00};
	this->opened = this->enobio.openDevice(mac);
	return this->opened;
}

BOOL Enobio::init(const int) {
	// it does not appear as if the Enobio has a way to only request a
	// subset of channels, so we would use this to create a mask on the
	// returned sample data.
	return true;
}

BOOL Enobio::start() {
	this->enobio.startStreaming();
	this->started = true;
	return this->started;
}

BOOL Enobio::acquire() {
	DWORD result;
	result = WaitForSingleObject(this->enobioData->hEvent, 1000);
	if (result != WAIT_OBJECT_0) {
		printf("Wait error (%d)\n",result);
		return false;
	} else {
		int nSamples = this->enobioData->nSamples;
		memcpy(this->samples, this->enobioData->buffer, CHANNELS*nSamples*sizeof(int));
		this->enobioData->nSamples = 0;
		return nSamples;
	}	
}

void Enobio::getdata(int *data, int n) {
	if(n >= BUFFER_SAMPLES*CHANNELS) {
		n = BUFFER_SAMPLES*CHANNELS;
	}
	memcpy(data, this->samples, n*sizeof(int));
}

unsigned long long Enobio::timestamp() {
	return this->enobioData->timestamp;
}

BOOL Enobio::stop() {
	this->enobio.stopStreaming();
	this->started = false;
	return true;
}

BOOL Enobio::close() {
	this->enobio.closeDevice();
	this->opened = false;
	return true;
}