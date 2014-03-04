
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
#define BOOST_TEST_MODULE MobilabSignalTests
#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "NonblockingSignal.hpp"
#include "MobilabSignal.hpp"
#include "Sample.hpp"

using namespace std;

//uint8_t mac1[RandomSignal::MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(MobilabSignalTest)
#if 0
BOOST_AUTO_TEST_CASE(test_create_delete)
{
  cout << "PynobioTest.test_create_delete" << endl;
  Enobio* signal = new Enobio();
  delete signal;//blockless_signal;
}

BOOST_AUTO_TEST_CASE(test_create_open_start_acquire_getdata_stop_close)
{
  cout << "Pynobio.test_create_open_start_acquire_getdata_stop_close " << endl;
  Enobio* signal = new Enobio();
  BOOST_VERIFY(signal->open(0));
  BOOST_VERIFY(signal->start());
  cout << "Started sleeping for 2 seconds ... " << endl;
  boost::this_thread::sleep(boost::posix_time::seconds(2));
  cout << "after sleep " << endl;
  size_t samples = 0;
  while (samples < 1)
    samples = signal->acquire();
    
  cout << "call to acquire returns --->" << samples  << "<--- " << endl;
  uint32_t* buffer = new uint32_t[samples];
  for(int i=0; i < samples; i++)
    buffer[i] = 0;
  
  signal->getdata(buffer, samples);
  for(int i=0; i < samples; i++) {
    BOOST_CHECK(buffer[i] != 0);
  }
  
  BOOST_VERIFY(signal->stop());
  BOOST_VERIFY(signal->close());
  boost::this_thread::sleep(boost::posix_time::seconds(5));
}

BOOST_AUTO_TEST_CASE(test_create_wrap_open_start_acquire_getdata_stop_close)
{
  cout << "Pynobio.test_create_wrap_open_start_acquire_getdata_stop_close " << endl;
  Enobio* ensig = new Enobio();
  NonblockingSignal* signal = new NonblockingSignal(ensig);
  BOOST_VERIFY(signal->open(0));
  BOOST_VERIFY(signal->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  size_t samples = 0;
  samples = signal->acquire();
  BOOST_CHECK(samples > 0);    
  uint32_t* buffer = new uint32_t[samples];
  for(int i=0; i < samples; i++)
    buffer[i] = 0;
  
  signal->getdata(buffer, samples);
  for(int i=0; i < samples; i++) {
    BOOST_CHECK(buffer[i] != 0);
  }
  
  BOOST_CHECK(signal->stop());
  BOOST_CHECK(signal->close());
  boost::this_thread::sleep(boost::posix_time::seconds(5));  
}
#endif
BOOST_AUTO_TEST_SUITE_END()
