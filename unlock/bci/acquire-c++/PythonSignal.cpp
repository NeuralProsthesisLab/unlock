
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

#include <boost/random/uniform_int_distribution.hpp>
#include <boost/assert.hpp>
#include <limits>

using namespace std;

#include "PythonSignal.hpp"

PythonSignal::PythonSignal(ISignal* pSignal, ITimer* pTimer)
  : mpSignal(pSignal), mpTimer(pTimer)
{
    BOOST_VERIFY(mpSignal != 0 && mpTimer != 0);
    mReturnedDataLog.open("PythonSignalLog.txt");
}

PythonSignal::~PythonSignal() {
  BOOST_VERIFY(mpSignal != 0);  
  delete mpSignal;
  mReturnedDataLog.close();
}

bool PythonSignal::open(boost::python::list macAddress) {
  BOOST_VERIFY(mpSignal != 0);
  uint8_t mac[6] = {0,0,0,0,0,0};  
  if(boost::python::extract<size_t>(macAddress.attr("__len__")()) >= 6) {
    for (int i = 5; i >= 0; i--) {
      mac[i] = boost::python::extract<uint8_t>(macAddress.pop());
    }
  }
  return mpSignal->open(mac);
}

bool PythonSignal::init(size_t channels) {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->init(channels);
}

size_t PythonSignal::channels() {
  BOOST_VERIFY(mpSignal != 0);
    return mpSignal->channels();  
}

bool PythonSignal::start() {
  BOOST_VERIFY(mpSignal != 0);  
    return mpSignal->start();  
}

size_t PythonSignal::acquire() {
  BOOST_VERIFY(mpSignal != 0);
  try {
    return mpSignal->acquire();
  } catch(...) {
    std::cerr << "PythonSignal.acquire ERROR: exception raised; returning 0 samples" << std::endl;
    return 0;
  }
}

std::vector<int32_t> PythonSignal::getdata(size_t samples) {
  BOOST_VERIFY(mpSignal != 0);
    std::vector<int32_t> ret = std::vector<int32_t>(samples);
    if(samples == 0) {
      return ret;
    }
    
    try {
      uint32_t* buffer = new uint32_t[samples];
      BOOST_VERIFY(buffer != 0);
      mpSignal->getdata(buffer, samples);
      for (size_t i = 0; i < samples; i++) {
        ret.push_back((int32_t)buffer[i]);
        mReturnedDataLog << (int32_t) ret.back() << " ";
        if((i+1) % mpSignal->channels() == 0) {
          mReturnedDataLog << endl;
        }

      }
      delete[] buffer;
      buffer = 0;
      return ret;
  } catch(...) {
    std::cerr << "PythonSignal.getdata ERROR: exception raised; returning empty samples vector " << std::endl;
  }
  return ret;
}

uint32_t PythonSignal::elapsedMicroSecs() {
  return mpTimer->elapsedMicroSecs();
}

uint64_t PythonSignal::timestamp() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->timestamp();
}

bool PythonSignal::stop() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->stop();
}

bool PythonSignal::close() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->close();
}

