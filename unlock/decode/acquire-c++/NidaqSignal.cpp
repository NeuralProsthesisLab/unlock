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

#include <stdio.h>
#include <NIDAQmx.h>

NidaqSignal::NidaqSignal() mTaskHandle(0), mpDataBuffer(0), mSamplesPerChunk(500) {
	channels(4);
}

NidaqSignal::~NidaqSignal() {
	if(mpData != 0) {
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
	mpDataBuffer = new float64[mSamplesPerChunk*mChannels]
}

size_t NidaqSignal::channels() {
	return mChannels;
}	

bool NidaqSignal::start() {
	int32 error=0;
	char  errorBuffer[2048]={'\0'};
	
	error = DAQmxCreateTask("",&mTaskHandle));
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.start: ERROR: " << errorBuffer << std::endl;
		return false;
	}
	
	error = DAQmxCreateAIVoltageChan(mTaskHandle,"Dev1/ai0","",DAQmx_Val_Cfg_Default,-10.0,10.0,DAQmx_Val_Volts,NULL);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.start: ERROR: " << errorBuffer << std::endl;
		return false;
	}

	error = DAQmxCfgSampClkTiming(mTaskHandle,"",1000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,mSamplesPerChannel);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.start: ERROR: " << errorBuffer << std::endl;
		return false;
	}	
	
	error = DAQmxStartTask(taskHandle);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.start: ERROR: " << errorBuffer << std::endl;
		return false;
	}
	return true;
}

size_t acquire() {
	int32 error=0;
	char  errorBuffer[2048]={'\0'};
	error = DAQmxReadAnalogF64(mTaskHandle,500, DAQmx_Val_WaitInfinitely, DAQmx_Val_GroupByChannel, mpDataBuffer, mChannels*mSampelsPerChannel, &read, NULL);
	if (DAQmxFailed(error)) {
    	DAQmxGetExtendedErrorInfo(errorBuffer,2048);
		std::cerr << "NidaqSignal.acquire: ERROR: " << errorBuffer << std::endl;
		return 0;
	}
	return &read;
}


void getdata(uint32_t* buffer, size_t samples) {
//	uint32_t* scaled = scale(mpDataBuffer);
	for(int i = 0; i < samples; i++) {
		buffer[i] = (uint32_t)mpDataBuffer[i];
	}
}

uint64_t timestamp() {	
}

bool stop() {
	DAQmxStopTask(mTaskHandle);
	DAQmxClearTask(mTaskHandle);
}

bool close() {
}
