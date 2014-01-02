
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

#ifndef PYNOBIO_HPP
#define PYNOBIO_HPP

#include <Windows.h>
//#include <boost/mutex.hpp>
#include <boost/thread.hpp>
#include <fstream>

#include "ISignal.hpp"
#include "ITimer.hpp"
#include "IEnobioSignalHandler.hpp"
#include "EnobioDataReceiver.hpp"
#include "EnobioStatusReceiver.hpp"
#include "Enobio3G.h"
#include "Channeldata.h"
#include "StatusData.h"
#include "Portability.hpp"

class DllExport EnobioSignalHandler : public ISignal, public IEnobioSignalHandler {
public:
    EnobioSignalHandler(Enobio3G* pEnobio3G, ITimer* pTimer);
    virtual ~EnobioSignalHandler();
    void setEnobioDataReceiver(EnobioDataReceiver* pDataReceiver);
    void setEnobioStatusReceiver(EnobioStatusReceiver* pStatusReceiver);
    
public: // IEnobioSignalHandler
    virtual void handleStatusData(StatusData* pStatusData);
    virtual void handleChannelData(ChannelData* pChannelData);
    
public: //ISignal
    virtual bool open(uint8_t* mac);
    virtual bool init(size_t channels);
    virtual size_t channels();
    virtual bool start();
    virtual size_t acquire();
    virtual void getdata(uint32_t* buffer, size_t samples);
    virtual uint64_t timestamp();
    bool stop();
    bool close();

private:
    Enobio3G* mpEnobio3G;
    ITimer* mpTimer;
    EnobioDataReceiver* mpDataReceiver;
    EnobioStatusReceiver* mpStatusReceiver;
    uint32_t* mpRawBuffer;
    uint32_t* mpSamples;
    size_t mNumSamples;
    size_t mNumChannels;
    uint64_t mTimeStamp;
    HANDLE mhEvent;
    boost::mutex mMutex;
    bool mOpened;
    bool mStarted;
    std::ofstream mRawEnobioLog;
};

#endif