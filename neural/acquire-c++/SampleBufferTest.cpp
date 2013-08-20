#include <boost/test/unit_test.hpp>
#include "Sample.hpp"

#include <iostream>

using namespace std;

BOOST_AUTO_TEST_SUITE(SampleBufferTest)

BOOST_AUTO_TEST_CASE(testSampleBuffer)
{
  cout << "SampleBufferTest.testSampleBuffer " << endl;
  SampleBuffer<uint32_t> sample_buffer;
  BOOST_CHECK(sample_buffer.maximumReservation() == SampleBuffer::RING_SIZE-1);   
}

BOOST_AUTO_TEST_SUITE_END()
