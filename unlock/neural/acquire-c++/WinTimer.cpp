#include <iostream>
#include "WinTimer.hpp"

//__declspec(dllimport) WINMMAPI MMRESULT WINAPI timeGetDevCaps( __out_bcount(cbtc) LPTIMECAPS ptc, __in UINT cbtc);

using namespace std;

WinTimer::WinTimer() : mTimerFreq(), mCounterStart() {}
WinTimer::~WinTimer() {}

void WinTimer::start() {
  QueryPerformanceFrequency(&mTimerFreq);
  QueryPerformanceCounter(&mCounterStart);
  cout<<"timerFreq_ = "<<mTimerFreq.QuadPart<<endl;
  cout<<"counterAtStart_ = "<<mCounterStart.QuadPart<<endl;
/*  TIMECAPS ptc;
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
  }*/
}

uint32_t WinTimer::elapsedCycles()
{
  LARGE_INTEGER c;
  QueryPerformanceCounter(&c);
  return static_cast<uint32_t>((c.QuadPart - mCounterStart.QuadPart));
}

uint32_t WinTimer::elapsedMilliSecs()
{
  if (mTimerFreq.QuadPart == 0) {
    return -1;
  } else {
    LARGE_INTEGER c;
    QueryPerformanceCounter(&c);
    return static_cast<uint32_t>(((c.QuadPart - mCounterStart.QuadPart)*1000)/ mTimerFreq.QuadPart);
  }
}

uint32_t WinTimer::elapsedMicroSecs()
{
  if (mTimerFreq.QuadPart == 0) {
    return -1;
  } else {
    LARGE_INTEGER c;
    QueryPerformanceCounter(&c);
    return static_cast<uint32_t>(((c.QuadPart - mCounterStart.QuadPart)*1000000)/mTimerFreq.QuadPart);
  }
}

int64_t WinTimer::getFrequency() {
  return mTimerFreq.QuadPart;
}

int64_t WinTimer::getStartValue() {
  return mCounterStart.QuadPart;
}

/*
int main()
{
  //Increasing the accuracy of Sleep to 1ms using timeBeginPeriod
//  timeBeginPeriod(1); //Add Winmm.lib in Project
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
} */