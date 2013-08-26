#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "NonblockingSignal.hpp"
#include "Pynobio.hpp"
#include "FakeSignal.hpp"
#include "Sample.hpp"

using namespace std;

uint8_t mac1[FakeSignal::MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(PynobioTest)

BOOST_AUTO_TEST_CASE(test_create_delete)
{
  cout << "PynobioTest.test_create_delete" << endl;
  Enobio* signal = new Enobio();
  delete signal;//blockless_signal;
}

BOOST_AUTO_TEST_CASE(test_create_wrap_delete)
{
  cout << "PynobioTest.test_create_delete" << endl;
  Enobio* signal = new Enobio();
  BOOST_AUTO_TEST_CASE(test_create_delete)
  delete signal;//blockless_signal;
}

BOOST_AUTO_TEST_SUITE_END()
