#include "usbamp.h"

USBamp::USBamp() {
	this->callSequence.push_back("UB-2010.06.10"); // serial of slave 2
	this->callSequence.push_back("UB-2009.07.08"); // serial of slave 1
	this->callSequence.push_back("UB-2009.07.09"); // serial of master
}

USBamp::~USBamp() {
}

bool USBamp::open(LPSTR port) {
	for(deque<LPSTR>::iterator serialNumber = this->callSequence.begin(); serialNumber != )

	this->devptr = GT_OpenDevice(port);
	return this->devptr != NULL;	
}

bool USBamp::init(const int ain, const int dio) {
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

	return GT_InitChannels(this->devptr, aCh, dCh);
}

bool USBamp::start() {
	return GT_StartAcquisition(this->devptr);
}

bool USBamp::acquire() {
	BOOL ret;
	ret = GT_GetData(this->devptr, &(this->datbuffer), &(this->ov));
	WaitForSingleObject(this->ov.hEvent, 1000); 
	return ret;
}

void USBamp::getdata(int *data, int n) {
	for(int i=0; i < n; i++) {
		data[i] = this->buffer[i];
	}
}

bool USBamp::stop() {
	return GT_StopAcquisition(this->devptr);
}

bool USBamp::close() {
	return GT_CloseDevice(this->devptr);
}
