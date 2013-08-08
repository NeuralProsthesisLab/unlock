
#define BOOST_TEST_MODULE NonblockingBCITest
#include <boost/test/included/unit_test.hpp>
#include "nonblocking_bci.hpp"
#include "fake_bci.hpp"
#include <iostream>

using namespace std;

uint8_t mac[MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(NonblockingBCITest)
 
BOOST_AUTO_TEST_CASE(test_create_delete)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_create_open_delete)
{
    FakeBCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    BOOST_CHECK(bci->open(mac));
    for (int i=0; i < MAC_ADDRESS_SIZE; i++)
        BOOST_CHECK(fbci->mLastMac[i] == mac[i]);
        
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_start_stop)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    BOOST_CHECK(bci->open(mac));    
    BOOST_CHECK(bci->start());
    BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_delete)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    BOOST_CHECK(bci->start());
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_start_delete1)
{
    BCI* fbci = new FakeBCI();// = new FakeBCI();
    NonblockingBCI* bci = new NonblockingBCI(fbci);
    bci->start();
    delete bci;
}
 
 

BOOST_AUTO_TEST_SUITE_END()
