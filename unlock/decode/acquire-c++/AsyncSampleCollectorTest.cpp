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
#include <boost/thread/thread.hpp>
#include <boost/atomic.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"
#include "IntegralWorkcontroller.hpp"
#include "RandomSignal.hpp"
#include "Sample.hpp"

using namespace std;
using namespace boost;
using namespace boost::lockfree;

BOOST_AUTO_TEST_SUITE(AsyncSampleCollectorTest)

BOOST_AUTO_TEST_CASE(test_create_destroy)
{
  cout << "AsyncSampleCollector.test_create_destroy " << endl;        
  RandomSignal fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[42];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>,  capacity<(42 - 1)> > queue;
  IntegralWorkController workController(1);

  AsyncSampleCollector* collector = new AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
							     &workController, pProducerSamples, 42, &sampleRingBuffer);
  delete collector;
}

BOOST_AUTO_TEST_CASE(test_create_copy)
{
  cout << "AsyncSampleCollector.test_create_copy " << endl;    
  RandomSignal fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[1339];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>,  capacity<(1338)> > queue;
  IntegralWorkController workController(1);
  IntegralWorkController workController1(1);

  AsyncSampleCollector c = AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
						&workController, pProducerSamples, 1339, &sampleRingBuffer);
  
  AsyncSampleCollector c1 = AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
						 &workController1, pProducerSamples, 1339, &sampleRingBuffer);
  
  AsyncSampleCollector c2(c);
  BOOST_VERIFY(c == c2);
  BOOST_VERIFY(c != c1);
  BOOST_VERIFY(!(c != c2));
  BOOST_VERIFY(!(c == c1));
  c = c1;
  BOOST_VERIFY(c != c2);
  BOOST_VERIFY(c == c1);
  c = c2;
  BOOST_VERIFY(c == c2);
  BOOST_VERIFY(c != c1);  
}

BOOST_AUTO_TEST_CASE(test_current_sample)
{
  cout << "AsyncSampleCollector.test_current_sample " << endl;    
  RandomSignal fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[1339];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>,  capacity<(1338)> > queue;
  IntegralWorkController workController(1);
  IntegralWorkController workController1(1);

  AsyncSampleCollector c = AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
						&workController, pProducerSamples, 1339, &sampleRingBuffer);  
  for(int i=0; i < 1338; i++) {
    BOOST_CHECK_EQUAL(i, c.currentSample());
    c.incrementCurrentSample();
  }
  
  c.incrementCurrentSample();
    
  for(int i=0; i < 1338; i++) {
    BOOST_CHECK_EQUAL(i, c.currentSample());
    c.incrementCurrentSample();
  }
  
  c.incrementCurrentSample();
  BOOST_CHECK_EQUAL(0, c.currentSample());

}

BOOST_AUTO_TEST_CASE(test_functor)
{
  cout << "AsyncSampleCollector.test_functor " << endl;
  RandomSignal fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[4200];
  SampleBuffer<uint32_t> sampleRingBuffer;
  boost::lockfree::spsc_queue<Sample<uint32_t> > queue(4200);
  IntegralWorkController workController(1);
  
  AsyncSampleCollector c = AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
						&workController, pProducerSamples, 4200, &sampleRingBuffer);
  c();
  BOOST_CHECK_EQUAL(1, fbci.mAcquireCount);
  BOOST_CHECK_EQUAL(1, fbci.mChannelsCount);
  BOOST_CHECK_EQUAL(1, fbci.mGetDataCount);
  BOOST_CHECK_EQUAL(pProducerSamples[0].sample(), fbci.mpLastGetData);
  BOOST_CHECK_EQUAL(pProducerSamples[0].length(), fbci.mLastChannels * fbci.mAcquireRet);  
  BOOST_CHECK_EQUAL(1, c.currentSample());
}

BOOST_AUTO_TEST_CASE(test_threaded_functor)
{
  cout << "AsyncSampleCollector.test_functor " << endl;
  RandomSignal fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[4200];
  Sample<uint32_t>* pConsumerSamples = new Sample<uint32_t>[4200];  
  SampleBuffer<uint32_t> sampleRingBuffer;
  boost::lockfree::spsc_queue<Sample<uint32_t> > queue(4200);
  IntegralWorkController workController(1);
  
  boost::thread t(AsyncSampleCollector((ISignal*)&fbci, (spsc_queue<Sample<uint32_t> >* )&queue,
				       &workController, pProducerSamples, 4200, &sampleRingBuffer));

  t.join();
 
  BOOST_CHECK_EQUAL(1, fbci.mAcquireCount);
  BOOST_CHECK_EQUAL(1, fbci.mChannelsCount);
  BOOST_CHECK_EQUAL(1, fbci.mGetDataCount);
  BOOST_CHECK_EQUAL(pProducerSamples[0].sample(), fbci.mpLastGetData);
  BOOST_CHECK_EQUAL(pProducerSamples[0].length(), fbci.mLastChannels * fbci.mAcquireRet);
 
  size_t count =  queue.pop(pConsumerSamples[0]);
  BOOST_CHECK_EQUAL(1, count);
  BOOST_CHECK_EQUAL(pProducerSamples[0].sample(), pConsumerSamples[0].sample());
  BOOST_CHECK_EQUAL(pProducerSamples[0].length(), pConsumerSamples[0].length());
}

BOOST_AUTO_TEST_SUITE_END()
