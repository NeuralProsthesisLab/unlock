// Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
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
#include <iostream>
#include <boost/assert.hpp>
#include "MobilabSignal.hpp"

MobilabSignal::MobilabSignal(int32_t ain, int32_t dio, std::string port)
	: mAin(ain), mDio(dio), mPort(port), mpGtec(0), mChannels(0) {
	mEventHandler.hEvent = CreateEvent(0,FALSE,FALSE,0);
	mEventHandler.Offset = 0;
	mEventHandler.OffsetHigh = 0;
}

MobilabSignal::~MobilabSignal() {
	stop();
}

bool MobilabSignal::open(uint8_t* mac) {
	return true;
}

bool MobilabSignal::init(size_t channels) {
	return true;
}

size_t MobilabSignal::channels() {
	return mChannels;
}

bool MobilabSignal::start() {
	mpGtec = GT_OpenDevice((LPSTR)mPort.c_str());	
	// activate analog and digital channels
	_AIN aCh;
	_DIO dCh;
	aCh.ain1 = mAin & 0x01;
	aCh.ain2 = (mAin >> 1) & 0x01;
	aCh.ain3 = (mAin >> 2) & 0x01;
	aCh.ain4 = (mAin >> 3) & 0x01;
	aCh.ain5 = (mAin >> 4) & 0x01;
	aCh.ain6 = (mAin >> 5) & 0x01;
	aCh.ain7 = (mAin >> 6) & 0x01;
	aCh.ain8 = (mAin >> 7) & 0x01;
	dCh.dio1_enable = mDio & 0x01;
	dCh.dio2_enable = (mDio >> 1) & 0x01;
	dCh.dio3_enable = (mDio >> 2) & 0x01;
	dCh.dio4_enable = (mDio >> 3) & 0x01;
	dCh.dio5_enable = (mDio >> 4) & 0x01;
	dCh.dio6_enable = (mDio >> 5) & 0x01;
	dCh.dio7_enable = (mDio >> 6) & 0x01;
	dCh.dio8_enable = (mDio >> 7) & 0x01;

	// create buffers for data acquisition
	if(mpBuffer != 0) {
		delete[] mpBuffer;
		mpBuffer = 0;
	}
	mChannels = 0;
	for(int i = 0; i < 8; i++) {
		mChannels += ((mAin >> i) & 0x01);
	}
	mpBuffer = new int16_t[mChannels];
	mDatBuffer.validPoints = 0;
	mDatBuffer.size = sizeof(int16_t)*mChannels;
	mDatBuffer.pBuffer = mpBuffer;

	bool init = GT_InitChannels(mpGtec, aCh, dCh);
	if(!init) {
		std::cerr << "MobilabSignal.start ERROR: GT_InitChannels failed " << std::endl;
		return false;
	}
	
	bool start = GT_StartAcquisition(mpGtec);
	if(!init) {
		std::cerr << "MobilabSignal.start ERROR: GT_StartAquisition failed " << std::endl;
		return false;
	}
	return true;
}

size_t MobilabSignal::acquire() {
	bool ret=false;
	ret = GT_GetData(mpGtec, &mDatBuffer, &mEventHandler);
	if(!ret) {
		std::cerr << "Mobilab.acquire ERROR: GT_GetData failed " << std::endl;
		return 0;
	}
	WaitForSingleObject(mEventHandler.hEvent, 1000); 
	return mChannels;
}

void MobilabSignal::getdata(uint32_t* buffer, size_t samples) {
	BOOST_ASSERT(samples == mChannels);
	for(size_t i=0; i < samples; i++) {
		buffer[i] = mpBuffer[i];
	}
}

uint64_t MobilabSignal::timestamp() {
	return 0;
}

bool MobilabSignal::stop() {
	bool ret = GT_StopAcquisition(mpGtec);
	if(!ret) {
		std::cerr << "MobilabSignal.stop ERROR: GT_StopAcquisition failed " << std::endl;		
		return false;
	}
	
	if(mpBuffer != 0) {
		delete[] mpBuffer;
		mpBuffer = 0;
	}
	
	ret = GT_CloseDevice(mpGtec);
	if(!ret) {
		std::cerr << "MobilabSignal.stop ERROR: GT_CloseDevice failed " << std::endl;
		return false;
	}
	return true;
}

bool MobilabSignal::close() {
	return true;
}