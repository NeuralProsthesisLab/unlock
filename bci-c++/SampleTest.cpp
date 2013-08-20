#include <boost/test/unit_test.hpp>
#include "Sample.hpp"

#include <iostream>

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
