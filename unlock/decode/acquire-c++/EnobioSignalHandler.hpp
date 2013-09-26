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