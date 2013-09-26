#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <boost/python/list.hpp>
#include <iostream>

#include "PythonSignal.hpp"
#include "RandomSignal.hpp"
#include "WinTimer.hpp"
#include "Sample.hpp"

using namespace std;


BOOST_AUTO_TEST_SUITE(PythonSignalTest)

BOOST_AUTO_TEST_CASE(pythion_signal_test_create_delete)
{
  cout << "PythonSignalTest.test_create_delete" << endl;
  PythonSignal* signal = new PythonSignal(new RandomSignal(), new WinTimer());
  delete signal;//blockless_signal;
}

BOOST_AUTO_TEST_CASE(python_signal_test_create_open_start_acquire_getdata_stop_close)
{
  cout << "Pynobio.test_create_open_start_acquire_getdata_stop_close " << endl;
  PythonSignal* signal = new PythonSignal(new RandomSignal(), new WinTimer());
  cout << "Before mac addr " << endl;
  BOOST_VERIFY(signal->start());
  cout << "After start " << endl;
  BOOST_VERIFY(signal->stop());
  BOOST_VERIFY(signal->close());
  cout << "After close " << endl;  
}

BOOST_AUTO_TEST_SUITE_END()
