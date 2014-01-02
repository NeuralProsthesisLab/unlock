
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

#ifndef ITIMER_HPP
#define ITIMER_HPP

#include <stdint.h>
#include "Portability.hpp"

class DllExport ITimer {
public:
    virtual ~ITimer() {}
    virtual void start()=0;
    virtual uint32_t elapsedCycles()=0;
    virtual uint32_t elapsedMilliSecs()=0;
    virtual uint32_t elapsedMicroSecs()=0;    
    virtual int64_t getFrequency()=0;
    virtual int64_t getStartValue()=0;
};

#endif

#if 0


#include <iostream>
#include <Windows.h>

using namespace std;

LARGE_INTEGER timerFreq_;
LARGE_INTEGER counterAtStart_;

void startTime()
{
  QueryPerformanceFrequency(&timerFreq_);
  QueryPerformanceCounter(&counterAtStart_);
  cout<<"timerFreq_ = "<<timerFreq_.QuadPart<<endl;
  cout<<"counterAtStart_ = "<<counterAtStart_.QuadPart<<endl;
  TIMECAPS ptc;
  UINT cbtc = 8;
  MMRESULT result = timeGetDevCaps(&ptc, cbtc);
  if (result == TIMERR_NOERROR)
  {
    cout<<"Minimum resolution = "<<ptc.wPeriodMin<<endl;
    cout<<"Maximum resolution = "<<ptc.wPeriodMax<<endl;
  }
  else
  {
    cout<<"result = TIMER ERROR"<<endl;
  }
}

unsigned int calculateElapsedTime()
{
  if (timerFreq_.QuadPart == 0)
  {
    return -1;
  }
  else
  {
    LARGE_INTEGER c;
    QueryPerformanceCounter(&c);
    return static_cast<unsigned int>( (c.QuadPart - counterAtStart_.QuadPart) * 1000 / timerFreq_.QuadPart );
  }
}

int main()
{
  //Increasing the accuracy of Sleep to 1ms using timeBeginPeriod
  timeBeginPeriod(1); //Add Winmm.lib in Project
  unsigned int diffTime = 0, lastTime = 0, newTime = 0;
  startTime();
  lastTime = calculateElapsedTime();
  cout<<"Start Time = "<<lastTime<<endl;

  Sleep(100);
  newTime = calculateElapsedTime();
  diffTime = newTime - lastTime;
  cout<<"Time after 100ms Sleep = "<<newTime<<", Difference = "<<diffTime<<endl;
  lastTime = newTime;

  Sleep(100);
  newTime = calculateElapsedTime();
  diffTime = newTime - lastTime;
  cout<<"Time after 100ms Sleep = "<<newTime<<", Difference = "<<diffTime<<endl;
  lastTime = newTime;

  Sleep(5);
  newTime = calculateElapsedTime();
  diffTime = newTime - lastTime;
  cout<<"Time after   5ms Sleep = "<<newTime<<", Difference = "<<diffTime<<endl;
  lastTime = newTime;

  Sleep(50);
  newTime = calculateElapsedTime();
  diffTime = newTime - lastTime;
  cout<<"Time after  50ms Sleep = "<<newTime<<", Difference = "<<diffTime<<endl;

  timeEndPeriod(1); //Must be called if timeBeginPeriod() was called
  return 0;
}
#endif