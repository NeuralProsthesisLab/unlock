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
#ifndef MOBILAB_SIGNAL_HPP
#define MOBILAB_SIGNAL_HPP

#include <stdint.h>
#include <string>
#include <Windows.h>
#include "gmobilabplus.h"
#include "ISignal.hpp"

class MobilabSignal : public ISignal {
public:
	MobilabSignal(int32_t ain, int32_t dio, std::string port);
	~MobilabSignal();
	virtual bool open(uint8_t*);
	virtual bool init(size_t channels);
    virtual size_t channels();
	virtual bool start();
	virtual size_t acquire();
	virtual void getdata(uint32_t* data, size_t samples);
    virtual uint64_t timestamp();
	virtual bool stop();
	virtual bool close();
private:
	HANDLE mpGtec;
	int16_t* mpBuffer;
    _BUFFER_ST mDatBuffer;
	OVERLAPPED mEventHandler;
    std::string mPort;
    size_t mChannels;
    int32_t mAin;
    int32_t mDio;
};

#endif
