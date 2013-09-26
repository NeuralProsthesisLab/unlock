
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

#include <boost/test/unit_test.hpp>
#include <boost/random/uniform_int_distribution.hpp>
#include <iostream>

#include "Sample.hpp"

using namespace std;

BOOST_AUTO_TEST_SUITE(SampleBufferTest)

BOOST_AUTO_TEST_CASE(testSampleBuffer)
{
  cout << "SampleBufferTest.testSampleBuffer " << endl;
  SampleBuffer<uint32_t> sample_buffer;
/*  
  for (int i=0; i < std::numeric_limits<uint32_t>::max(); i++) {
    boost::random::uniform_int_distribution<> dist(1, std::numeric_limits<int32_t>::max());
    uint32_t samples = (uint32_t)dist(gen);
    if (samples > 0) {
      if (samples > mpRingBuffer->maximumReservation()) {
        cerr << "AsyncSampleCollector.operator()(): WARNING: samples acquire == " << samples << ", but the ring size == " << mpRingBuffer->maximumReservation() << " dropping extra requests " << endl;
        samples = mpRingBuffer->maximumReservation();
      }
      
      uint32_t* pBuffer = mpRingBuffer->reserve(samples);
      if (pBuffer == 0) {
	cerr << "AsyncSampleCollector.operator()(): ERROR: mpRingBuffer failed to reserve buffer; dropping these samples " << endl;
	continue;
      }
      for(int j = 0; j < samples; j++)
        pBuffer[i] = 1;
    }
    */
}

BOOST_AUTO_TEST_SUITE_END()
