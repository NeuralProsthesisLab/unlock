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
//
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

#include <string>
#include <iostream>
#include "NidaqSignal.hpp"

NidaqSignal::NidaqSignal() : mTaskHandle(0), mpDataBuffer(0), mSamplesPerChannelPerBatch(500) {
	init(4);
}

NidaqSignal::~NidaqSignal() {
	if(mpDataBuffer != 0) {
		delete [] mpDataBuffer;
	}	
}

bool NidaqSignal::open(uint8_t* mac) {
	return true;	
}

bool NidaqSignal::init(size_t channels) {
	if(mpDataBuffer != 0) {
		delete [] mpDataBuffer;
	}
	mChannels = channels;
	mpDataBuffer = new float64[mSamplesPerChannelPerBatch*mChannels];
	return true;
}

size_t NidaqSignal::channels() {
	return mChannels;
}	

bool NidaqSignal::start() {
	int32 error=0;
	char  errorBuffer[2048]={'\0'};
	std::string prefix = "NidaqSignal.start: ERROR: ";
	
	error = DAQmxCreateTask("",&mTaskHandle);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << prefix << errorBuffer << std::endl;
		return false;
	}

	error = DAQmxCreateAIVoltageChan(mTaskHandle,"Dev1/ai0:3","", DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,NULL);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << prefix << errorBuffer << std::endl;
		return false;
	}

	error = DAQmxCfgSampClkTiming(mTaskHandle,"",1000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,mSamplesPerChannelPerBatch);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << prefix << errorBuffer << std::endl;
		return false;
	}	
	
	error = DAQmxStartTask(mTaskHandle);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << prefix << errorBuffer << std::endl;
		return false;
	}
	return true;
}

size_t NidaqSignal::acquire() {
	int32 error=0;
	int32 read=0;
	char  errorBuffer[2048]={'\0'};
/*	error = DAQmxReadAnalogF64(mTaskHandle, mSamplesPerChannelPerBatch, DAQmx_Val_WaitInfinitely,
							   DAQmx_Val_GroupByChannel, mpDataBuffer, mChannels*mSamplesPerChannelPerBatch,
							   &read, NULL);*/
	error = DAQmxReadAnalogF64(mTaskHandle, mSamplesPerChannelPerBatch, DAQmx_Val_WaitInfinitely,
							   DAQmx_Val_GroupByScanNumber, mpDataBuffer, mChannels*mSamplesPerChannelPerBatch,
							   &read, NULL);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.acquire: ERROR: " << errorBuffer << std::endl;
		return 0;
	}
	return (size_t)read*mChannels;
}

void NidaqSignal::getdata(uint32_t* buffer, size_t samples) {
	for(int i = 0; i < samples; i++) {
		buffer[i] = (uint32_t)(mpDataBuffer[i] * 32768 / 10);
	}
}

uint64_t NidaqSignal::timestamp() {
	return -1;
}

bool NidaqSignal::stop() {
	DAQmxStopTask(mTaskHandle);
	DAQmxClearTask(mTaskHandle);
	return true;
}

bool NidaqSignal::close() {
	return true;
}
