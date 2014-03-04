
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
#define BOOST_TEST_MODULE RandomSignalTests
#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "RandomSignal.hpp"
#include "Sample.hpp"

using namespace std;

uint8_t mac[RandomSignal::MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(RandomSignalTest)

BOOST_AUTO_TEST_CASE(test_create_delete)
{
  cout << "RandomSignalTest.test_create_delete" << endl;
  ISignal* fbci = new RandomSignal();
  delete fbci;
}

BOOST_AUTO_TEST_CASE(test_create_open_delete)
{
  cout << "RandomSignalTest.test_create_open_delete" << endl;
  RandomSignal* fbci = new RandomSignal();
  BOOST_CHECK(fbci->open(mac));
  for (int i=0; i < RandomSignal::MAC_ADDRESS_SIZE; i++)
    BOOST_CHECK_EQUAL(mac[i], fbci->mLastMac[i]);
        
  delete fbci;
}

BOOST_AUTO_TEST_CASE(test_create_open_fail_delete)
{
  cout << "RandomSignalTest.test_create_open_fail_delete" << endl;
  RandomSignal* bci = new RandomSignal();
  bci->mOpenRet = false;
  mac[0] = 0xff;
  BOOST_CHECK(!bci->open(mac));
  for (int i=0; i < RandomSignal::MAC_ADDRESS_SIZE; i++)
    BOOST_CHECK_EQUAL(mac[i], bci->mLastMac[i]);
        
  delete bci;
}

BOOST_AUTO_TEST_CASE(test_open_start_stop)
{
  cout << "RandomSignalTest.test_open_start_stop " << endl;
  RandomSignal* bci = new RandomSignal();
  BOOST_CHECK(bci->open(mac));
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));    
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_stop)
{
  cout << "RandomSignalTest.test_start_stop " << endl;
  RandomSignal* bci = new RandomSignal();
  BOOST_CHECK(bci->start());
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_acquire_stop)
{
  cout << "RandomSignalTest.test_start_acquire_stop " << endl;
  RandomSignal* bci = new RandomSignal();
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, bci->mStartCount);
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= bci->mAcquireCount);
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_3x_acquire_stop)
{
  cout << "RandomSignalTest.test_start_3x_acquire_stop " << endl;
  RandomSignal* bci = new RandomSignal();
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, bci->mStartCount);
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= bci->mAcquireCount);
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_3x_acquire_stop_stop)
{
  cout << "RandomSignalTest.test_start_3x_acquire_stop " << endl;
  RandomSignal* bci = new RandomSignal();
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, bci->mStartCount);
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(bci->mAcquireRet <= bci->acquire());
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= bci->mAcquireCount);
  BOOST_CHECK(bci->stop());
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_delete)
{
  cout << "RandomSignalTest.test_start_delete " << endl;
  ISignal* bci = new RandomSignal();
  BOOST_CHECK(bci->start());
  delete bci;
}
BOOST_AUTO_TEST_SUITE_END()
