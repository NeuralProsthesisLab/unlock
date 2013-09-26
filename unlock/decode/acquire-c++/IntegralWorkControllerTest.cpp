#include <boost/test/unit_test.hpp>
#include "IntegralWorkController.hpp"

#include <iostream>

using namespace std;

BOOST_AUTO_TEST_SUITE(IntegralWorkControllerTest)

BOOST_AUTO_TEST_CASE(testIntegralWorkController)
{
  cout << "IntegralWorkControllerTest.testIntegralWorkController " << endl;
  IntegralWorkController iwc(0);
  BOOST_CHECK_EQUAL(false, iwc.doWork());
  BOOST_CHECK_EQUAL(false, iwc.doWork());
  BOOST_CHECK_EQUAL(false, iwc.doWork());    
    
  IntegralWorkController iwc1(1);
  BOOST_CHECK_EQUAL(true, iwc1.doWork());
  BOOST_CHECK_EQUAL(false, iwc1.doWork());
  BOOST_CHECK_EQUAL(false, iwc1.doWork());
    
  IntegralWorkController iwc2(2);
  BOOST_CHECK_EQUAL(true, iwc2.doWork());
  BOOST_CHECK_EQUAL(true, iwc2.doWork());    
  BOOST_CHECK_EQUAL(false, iwc2.doWork());
  BOOST_CHECK_EQUAL(false, iwc2.doWork());
}

BOOST_AUTO_TEST_SUITE_END()
