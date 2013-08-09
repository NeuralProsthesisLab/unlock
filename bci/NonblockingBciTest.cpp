#include <boost/test/unit_test.hpp>
#include <boost/thread/thread.hpp>
#include <iostream>

#include "NonblockingBci.hpp"
#include "FakeBci.hpp"
#include "Sample.hpp"

using namespace std;

uint8_t mac[FakeBci::MAC_ADDRESS_SIZE] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };

BOOST_AUTO_TEST_SUITE(NonblockingBciTest)

BOOST_AUTO_TEST_CASE(test_create_delete)
{
    Bci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_create_open_delete)
{
    FakeBci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    BOOST_CHECK(bci->open(mac));
    for (int i=0; i < FakeBci::MAC_ADDRESS_SIZE; i++)
        BOOST_CHECK(fbci->mLastMac[i] == mac[i]);
        
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_create_open_fail_delete)
{
    FakeBci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    fbci->mOpenRet = false;
    mac[0] = 0xff;
    BOOST_CHECK(!bci->open(mac));
    for (int i=0; i < FakeBci::MAC_ADDRESS_SIZE; i++)
        BOOST_CHECK(fbci->mLastMac[i] == mac[i]);
        
    delete bci;
}
/*
BOOST_AUTO_TEST_CASE(test_open_start_stop)
{
    FakeBci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    BOOST_CHECK(bci->open(mac));    
    BOOST_CHECK(bci->start());
    boost::this_thread::sleep(boost::posix_time::seconds(1));    
    BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_stop)
{
    FakeBci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    BOOST_CHECK(bci->start());
    BOOST_CHECK(bci->stop());
}


BOOST_AUTO_TEST_CASE(test_start_acquire_stop)
{
    FakeBci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    BOOST_CHECK(bci->start());
    BOOST_CHECK(fbci->mStartCount == 1);
    BOOST_CHECK(bci->acquire() == fbci->mAcquireRet);
    BOOST_CHECK(fbci->mAcquireCount == 1);
    BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_delete)
{
    Bci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    BOOST_CHECK(bci->start());
    delete bci;
}

BOOST_AUTO_TEST_CASE(test_start_delete1)
{
    Bci* fbci = new FakeBci();
    NonblockingBci* bci = new NonblockingBci(fbci);
    bci->start();
    delete bci;
}
*/
BOOST_AUTO_TEST_SUITE_END()
