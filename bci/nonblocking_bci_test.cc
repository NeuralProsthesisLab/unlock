
#define BOOST_TEST_MODULE NonblockingBCITest
#include <boost/test/included/unit_test.hpp>
#include "nonblocking_bci.hpp"
#include "fake_bci.hpp"
#include <iostream>

using namespace std;

struct NonblockingBCIWrapper
{
    int m;
 
    NonblockingBCIWrapper() : m(2)
    {
        BOOST_TEST_MESSAGE("setup mass");
    }
 
    ~NonblockingBCIWrapper()
    {
        BOOST_TEST_MESSAGE("teardown mass");
    }
};
 
BOOST_FIXTURE_TEST_SUITE(NonblockingBCITest, NonblockingBCIWrapper)
 
BOOST_AUTO_TEST_CASE(test_create_delete)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_start_stop)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    bci->start();
    bci->stop();
}

BOOST_AUTO_TEST_CASE(test_start_delete)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    bci->start();
    delete bci;
}
 
BOOST_AUTO_TEST_SUITE_END()
