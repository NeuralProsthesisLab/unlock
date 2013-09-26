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
