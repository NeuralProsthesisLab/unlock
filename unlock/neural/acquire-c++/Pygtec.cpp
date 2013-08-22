#include "pygtec.h"

MOBIlab::MOBIlab() {
	// init device handler
	this->devptr = NULL;

	// device event handler		
	this->ov.hEvent = CreateEvent(NULL,FALSE,FALSE,NULL);
	this->ov.Offset = 0;
	this->ov.OffsetHigh = 0;	
}

MOBIlab::~MOBIlab() {
	this->stop();
	this->close();	
}

BOOL MOBIlab::open(LPSTR port) {
	this->devptr = GT_OpenDevice(port);
	return this->devptr != NULL;	
}

BOOL MOBIlab::init(const int ain, const int dio) {
	// activate analog and digital channels
	_AIN aCh;
	_DIO dCh;
	aCh.ain1 = ain & 0x01;
	aCh.ain2 = (ain >> 1) & 0x01;
	aCh.ain3 = (ain >> 2) & 0x01;
	aCh.ain4 = (ain >> 3) & 0x01;
	aCh.ain5 = (ain >> 4) & 0x01;
	aCh.ain6 = (ain >> 5) & 0x01;
	aCh.ain7 = (ain >> 6) & 0x01;
	aCh.ain8 = (ain >> 7) & 0x01;
	dCh.dio1_enable = dio & 0x01;
	dCh.dio2_enable = (dio >> 1) & 0x01;
	dCh.dio3_enable = (dio >> 2) & 0x01;
	dCh.dio4_enable = (dio >> 3) & 0x01;
	dCh.dio5_enable = (dio >> 4) & 0x01;
	dCh.dio6_enable = (dio >> 5) & 0x01;
	dCh.dio7_enable = (dio >> 6) & 0x01;
	dCh.dio8_enable = (dio >> 7) & 0x01;

	// create buffers for data acquisition
	if(this->buffer != NULL) {
		delete[] this->buffer;
	}
	int nChannels = 0;
	for(int i = 0; i < 8; i++) {
		nChannels += ((ain >> i) & 0x01);
	}
	this->buffer = new short[nChannels];
	this->datbuffer.validPoints = 0;
	this->datbuffer.size = sizeof(short)*nChannels;
	this->datbuffer.pBuffer = this->buffer;

	return GT_InitChannels(this->devptr, aCh, dCh);
}

BOOL MOBIlab::start() {
	return GT_StartAcquisition(this->devptr);
}

BOOL MOBIlab::acquire() {
	BOOL ret;
	ret = GT_GetData(this->devptr, &(this->datbuffer), &(this->ov));
	WaitForSingleObject(this->ov.hEvent, 1000); 
	return ret;
}

void MOBIlab::getdata(int *data, int n) {
	for(int i=0; i < n; i++) {
		data[i] = this->buffer[i];
	}
}

BOOL MOBIlab::stop() {
	return GT_StopAcquisition(this->devptr);
}

BOOL MOBIlab::close() {
	if(this->buffer != NULL) {
		delete[] this->buffer;
	}
	return GT_CloseDevice(this->devptr);
}