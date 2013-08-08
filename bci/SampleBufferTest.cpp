#include <boost/test/unit_test.hpp>
#include "Sample.hpp"

#include <iostream>

using namespace std;

BOOST_AUTO_TEST_SUITE(SampleTest)

BOOST_AUTO_TEST_CASE(test_sample_buffer)
{
    SampleBuffer<uint32_t> sample_buffer;
    BOOST_CHECK(sample_buffer.maximum_reservation() == RING_SIZE-1);   
}

BOOST_AUTO_TEST_SUITE_END()
