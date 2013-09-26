#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "NiDaqMx.hpp"

BOOST_AUTO_TEST_SUITE(DaqTest)

BOOST_AUTO_TEST_CASE(daq_test)
{
  std::cout << "DAQTest.." << std::endl;
  daq_function();
}

BOOST_AUTO_TEST_SUITE_END()
