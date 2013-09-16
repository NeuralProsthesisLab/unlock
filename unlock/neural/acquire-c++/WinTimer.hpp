#ifndef WIN_TIMER_HPP
#define WIN_TIMER_HPP

#include <Windows.h>

#include "Portability.hpp"
#include "ITimer.hpp"


class DllExport WinTimer : public ITimer {
public:
    WinTimer();
    virtual ~WinTimer();
    virtual void start();
    virtual uint32_t elapsedCycles();
    virtual uint32_t elapsedMilliSecs();
    virtual uint32_t elapsedMicroSecs();    
    virtual int64_t getFrequency();
    virtual int64_t getStartValue();
    
private:
    LARGE_INTEGER mTimerFreq;
    LARGE_INTEGER mCounterStart;
};

#endif