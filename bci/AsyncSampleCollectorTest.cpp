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

BOOST_AUTO_TEST_CASE(test)
{
  FakeBci fbci;
  Sample<uint32_t>* pProducerSamples = new Sample<uint32_t>[42];
  SampleBuffer<uint32_t> sampleRingBuffer;
  spsc_queue<Sample<uint32_t>*,  capacity<(42 - 1)> > queue;
  IntegralWorkController workController(1);

  AsyncSampleCollector collector = AsyncSampleCollector((IBci*)&fbci, (spsc_queue<Sample<uint32_t>* >* )&queue,
                                            &workController, pProducerSamples, &sampleRingBuffer);
  collector();
}

BOOST_AUTO_TEST_SUITE_END()
