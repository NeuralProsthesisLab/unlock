
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
#include "IntegralWorkController.hpp"

#include <iostream>

using namespace std;

BOOST_AUTO_TEST_SUITE(IntegralWorkControllerTest)

BOOST_AUTO_TEST_CASE(testIntegralWorkController)
{
  cout << "IntegralWorkControllerTest.testIntegralWorkController " << endl;
  IntegralWorkController iwc(0);
  BOOST_CHECK_EQUAL(false, iwc.doWork());
  BOOST_CHECK_EQUAL(false, iwc.doWork());
  BOOST_CHECK_EQUAL(false, iwc.doWork());    
    
  IntegralWorkController iwc1(1);
  BOOST_CHECK_EQUAL(true, iwc1.doWork());
  BOOST_CHECK_EQUAL(false, iwc1.doWork());
  BOOST_CHECK_EQUAL(false, iwc1.doWork());
    
  IntegralWorkController iwc2(2);
  BOOST_CHECK_EQUAL(true, iwc2.doWork());
  BOOST_CHECK_EQUAL(true, iwc2.doWork());    
  BOOST_CHECK_EQUAL(false, iwc2.doWork());
  BOOST_CHECK_EQUAL(false, iwc2.doWork());
}

BOOST_AUTO_TEST_SUITE_END()
