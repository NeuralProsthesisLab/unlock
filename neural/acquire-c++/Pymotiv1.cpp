#include "pymotiv.h"

EPOC::EPOC() {
	this->eEvent = EE_EmoEngineEventCreate();
	this->ready = false;
	this->nChannels = 0;
	this->channels = NULL;
	this->samples = NULL;
	this->userId = 0;
	this->closed = false;
}

EPOC::~EPOC() {
	this->stop();
	if(!this->closed) {
	    this->close();
	}
}

BOOL EPOC::open() {
	return (EE_EngineConnect() == EDK_OK);
}

BOOL EPOC::init(const int) {
	// need to have a smart way to indicate channels of interest
	this->nChannels = 3;
	this->channels = new EE_DataChannel_t[this->nChannels];
	this->channels[0] = ED_O1;
	this->channels[1] = ED_O2;
	this->channels[2] = ED_F8;

	this->hData = EE_DataCreate();
	return (EE_DataSetBufferSizeInSec(1) == EDK_OK);
	
	/*
	EE_DataChannel_t targetChannelList[] = {
		ED_COUNTER,
		ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, 
		ED_P7, ED_O1, ED_O2, ED_P8, ED_T8, 
		ED_FC6, ED_F4, ED_F8, ED_AF4, ED_GYROX, ED_GYROY, ED_TIMESTAMP, 
		ED_FUNC_ID, ED_FUNC_VALUE, ED_MARKER, ED_SYNC_SIGNAL
	};
	*/
}

BOOL EPOC::start() {
	
	// A user needs to be registered before acquisition can happen
	while(EE_EngineGetNextEvent(this->eEvent) != EDK_OK) {;}
	
	EE_Event_t eventType = EE_EmoEngineEventGetType(this->eEvent);
	EE_EmoEngineEventGetUserId(this->eEvent, &this->userId);
	if(eventType == EE_UserAdded) {
		EE_DataAcquisitionEnable(this->userId, true);
		return (this->ready = true);
	} else {
		return false;
	}
}

BOOL EPOC::acquire() {
	if(this->ready) {		
		EE_DataUpdateHandle(this->userId, this->hData);
		unsigned int nSamples = 0;
		EE_DataGetNumberOfSample(this->hData, &nSamples);

		if (nSamples != 0) {
			delete[] this->samples;
			this->samples = new double[this->nChannels*nSamples];
				for(int i=0; i < this->nChannels; ++i) {
					EE_DataGet(hData, this->channels[i], samples + i*nSamples, nSamples);
				}	
			return nSamples;
		}
	}
	return false;
}

void EPOC::getdata(int *data, int n) {
	for(int i=0; i < n; ++i) {
		data[i] = (int)this->samples[i];
	}
}

BOOL EPOC::stop() {
	this->ready = false;
	return true;
}

BOOL EPOC::close() {
	delete[] this->channels;
	delete[] this->samples;
	EE_DataFree(this->hData);
	EE_EngineDisconnect();
	EE_EmoEngineEventFree(this->eEvent);
	this->closed = true;
	return true;
}