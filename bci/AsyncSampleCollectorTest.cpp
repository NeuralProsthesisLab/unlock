#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <boost/atomic.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"
#include "IntegralWorkcontroller.hpp"
#include "FakeBci.hpp"
#include "Sample.hpp"

using namespace std;
using namespace boost;
using namespace boost::lockfree;

BOOST_AUTO_TEST_SUITE(AsyncSampleCollectorTest)

BOOST_AUTO_TEST_CASE(test_create_destroy)
{
  FakeBci fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[42];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>*,  capacity<(42 - 1)> > queue;
  IntegralWorkController workController(1);

  AsyncSampleCollector* collector = new AsyncSampleCollector((IBci*)&fbci, (spsc_queue<Sample<uint32_t>* >* )&queue,
                                            &workController, pProducerSamples, &sampleRingBuffer);
  delete collector;
}

BOOST_AUTO_TEST_CASE(test_create_copy)
{
  FakeBci fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[42];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>*,  capacity<(42 - 1)> > queue;
  IntegralWorkController workController(1);
  IntegralWorkController workController1(1);

  AsyncSampleCollector c = AsyncSampleCollector((IBci*)&fbci, (spsc_queue<Sample<uint32_t>* >* )&queue,
                                            &workController, pProducerSamples, &sampleRingBuffer);  
  AsyncSampleCollector c1 = AsyncSampleCollector((IBci*)&fbci, (spsc_queue<Sample<uint32_t>* >* )&queue,
                                            &workController1, pProducerSamples, &sampleRingBuffer);  
  AsyncSampleCollector c2(c);
  BOOST_VERIFY(c == c2);
  BOOST_VERIFY(c != c1);
  BOOST_VERIFY(!(c != c2));
  BOOST_VERIFY(!(c == c1));  
}

BOOST_AUTO_TEST_SUITE_END()
