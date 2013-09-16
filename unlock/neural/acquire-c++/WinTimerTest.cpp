#include <boost/test/unit_test.hpp>
#include <boost/thread.hpp>
#include <iostream>
#include <cstdint>

#include "WinTimer.hpp"

using namespace std;

BOOST_AUTO_TEST_SUITE(WinTimerTest)
 
BOOST_AUTO_TEST_CASE(testWinTimer)
{
  cout << "WinTimerTest.testWinTimer " << endl;
  WinTimer timer;
  timer.start();

  cout << " Elapsed cycles = " << timer.elapsedCycles() << endl;
  cout << " Elapsed millis = " << timer.elapsedMilliSecs() << endl;
  cout << " Elapsed micros = " << timer.elapsedMicroSecs() << endl;
  cout << " Frequence = " << timer.getFrequency() << endl;
  
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  
  cout << " Elapsed cycles = " << timer.elapsedCycles() << endl;
  cout << " Elapsed millis = " << timer.elapsedMilliSecs() << endl;
  cout << " Elapsed micros = " << timer.elapsedMicroSecs() << endl;
  int32_t value = timer.elapsedMilliSecs();
  int32_t value1 = timer.elapsedMicroSecs();
  // this is really a test of the boost sleep function, that executes the code.
  BOOST_VERIFY(value >= 900 && value <= 1100);
  BOOST_VERIFY(value1 >= 900000 && value <= 1100000);
  
}

BOOST_AUTO_TEST_SUITE_END()
