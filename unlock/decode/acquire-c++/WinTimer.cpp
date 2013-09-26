
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

#include <iostream>
#include "WinTimer.hpp"

//__declspec(dllimport) WINMMAPI MMRESULT WINAPI timeGetDevCaps( __out_bcount(cbtc) LPTIMECAPS ptc, __in UINT cbtc);

using namespace std;

WinTimer::WinTimer() : mTimerFreq(), mCounterStart() {}
WinTimer::~WinTimer() {}

void WinTimer::start() {
  QueryPerformanceFrequency(&mTimerFreq);
  QueryPerformanceCounter(&mCounterStart);
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
