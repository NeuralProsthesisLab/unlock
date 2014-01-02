
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
#include <iostream>
#include <cstdint>

#include "Sample.hpp"

using namespace std;

BOOST_AUTO_TEST_SUITE(SampleTest)
 
BOOST_AUTO_TEST_CASE(testSample)
{
  cout << "SampleTest.testSample " << endl;
  uint8_t test_sample[6] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };
    
  Sample<uint8_t>* sample = new Sample<uint8_t>();
  sample->configure((uint8_t*)test_sample, 6);
  BOOST_CHECK(sample->length() == 6);
  BOOST_CHECK(sample->sample() == test_sample);
    
  Sample<uint8_t> s1;
  s1.configure((uint8_t*)test_sample, 6);
  BOOST_CHECK(s1.length() == 6);
  BOOST_CHECK(s1.sample() == test_sample);
    
  Sample<uint8_t> s2(s1);
  BOOST_CHECK(s2.length() == 6);
  BOOST_CHECK(s2.sample() == test_sample);
    
  uint8_t test_sample1[9] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9 };
    
  s2.configure(test_sample1, 9);
  BOOST_CHECK(s2.length() == 9);
  BOOST_CHECK(s2.sample() == test_sample1);
    
  s1 = s2;
  BOOST_CHECK(s1.length() == 9);
  BOOST_CHECK(s1.sample() == test_sample1);
}

BOOST_AUTO_TEST_SUITE_END()
