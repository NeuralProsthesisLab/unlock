#include <boost/test/unit_test.hpp>
#include "ManagedWorkController.hpp"

#include <iostream>

using namespace std;

BOOST_AUTO_TEST_SUITE(ManagedWorkControllerTest)

BOOST_AUTO_TEST_CASE(testManagedWorkController)
{
    cout << "ManagedWorkControllerTest.testManagedWorkController " << endl;
    ManagedWorkController mwc(true);
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());    

    mwc.setDoWorkState(false);
    BOOST_CHECK_EQUAL(false, mwc.doWork());
    BOOST_CHECK_EQUAL(false, mwc.doWork());
    BOOST_CHECK_EQUAL(false, mwc.doWork());

    mwc.setDoWorkState(true);
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    
    mwc.setDoWorkState(true);
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());
    BOOST_CHECK_EQUAL(true, mwc.doWork());
}

BOOST_AUTO_TEST_SUITE_END()
