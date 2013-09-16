#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "NonblockingSignal.hpp"
#include "EnobioSignalHandler.hpp"
#include "RandomSignal.hpp"
#include "Sample.hpp"

using namespace std;

uint8_t mac1[RandomSignal::MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(EnobioSignalHandlerTest)
#if 0
BOOST_AUTO_TEST_CASE(test_create_delete)
{
  cout << "PynobioTest.test_create_delete" << endl;
  Enobio* signal = new Enobio();
  delete signal;//blockless_signal;
}

BOOST_AUTO_TEST_CASE(test_create_open_start_acquire_getdata_stop_close)
{
  cout << "Pynobio.test_create_open_start_acquire_getdata_stop_close " << endl;
  Enobio* signal = new Enobio();
  BOOST_VERIFY(signal->open(0));
  BOOST_VERIFY(signal->start());
  cout << "Started sleeping for 2 seconds ... " << endl;
  boost::this_thread::sleep(boost::posix_time::seconds(2));
  cout << "after sleep " << endl;
  size_t samples = 0;
  while (samples < 1)
    samples = signal->acquire();
    
  cout << "call to acquire returns --->" << samples  << "<--- " << endl;
  uint32_t* buffer = new uint32_t[samples];
  for(int i=0; i < samples; i++)
    buffer[i] = 0;
  
  signal->getdata(buffer, samples);
  for(int i=0; i < samples; i++) {
    BOOST_CHECK(buffer[i] != 0);
  }
  
  BOOST_VERIFY(signal->stop());
  BOOST_VERIFY(signal->close());
  boost::this_thread::sleep(boost::posix_time::seconds(5));
}

BOOST_AUTO_TEST_CASE(test_create_wrap_open_start_acquire_getdata_stop_close)
{
  cout << "Pynobio.test_create_wrap_open_start_acquire_getdata_stop_close " << endl;
  Enobio* ensig = new Enobio();
  NonblockingSignal* signal = new NonblockingSignal(ensig);
  BOOST_VERIFY(signal->open(0));
  BOOST_VERIFY(signal->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  size_t samples = 0;
  samples = signal->acquire();
  BOOST_CHECK(samples > 0);    
  uint32_t* buffer = new uint32_t[samples];
  for(int i=0; i < samples; i++)
    buffer[i] = 0;
  
  signal->getdata(buffer, samples);
  for(int i=0; i < samples; i++) {
    BOOST_CHECK(buffer[i] != 0);
  }
  
  BOOST_CHECK(signal->stop());
  BOOST_CHECK(signal->close());
  boost::this_thread::sleep(boost::posix_time::seconds(5));  
}
#endif
BOOST_AUTO_TEST_SUITE_END()
