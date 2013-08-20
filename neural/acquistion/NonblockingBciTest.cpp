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
  cout << "NonblockingBciTest.test_create_delete" << endl;
  IBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  delete bci;
}

BOOST_AUTO_TEST_CASE(test_create_open_delete)
{
  cout << "NonblockingBciTest.test_create_open_delete" << endl;    
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->open(mac));
  for (int i=0; i < FakeBci::MAC_ADDRESS_SIZE; i++)
    BOOST_CHECK_EQUAL(mac[i], fbci->mLastMac[i]);
        
  delete bci;
}

BOOST_AUTO_TEST_CASE(test_create_open_fail_delete)
{
  cout << "NonblockingBciTest.test_create_open_fail_delete" << endl;        
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  fbci->mOpenRet = false;
  mac[0] = 0xff;
  BOOST_CHECK(!bci->open(mac));
  for (int i=0; i < FakeBci::MAC_ADDRESS_SIZE; i++)
    BOOST_CHECK_EQUAL(mac[i], fbci->mLastMac[i]);
        
  delete bci;
}

BOOST_AUTO_TEST_CASE(test_open_start_stop)
{
  cout << "NonblockingBciTest.test_open_start_stop " << endl;        
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->open(mac));    
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));    
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_stop)
{
  cout << "NonblockingBciTest.test_start_stop " << endl;            
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->start());
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_acquire_stop)
{
  cout << "NonblockingBciTest.test_start_acquire_stop " << endl;            
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, fbci->mStartCount);
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= fbci->mAcquireCount);
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_3x_acquire_stop)
{
  cout << "NonblockingBciTest.test_start_3x_acquire_stop " << endl;            
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, fbci->mStartCount);
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());    
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= fbci->mAcquireCount);
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_3x_acquire_stop_stop)
{
  cout << "NonblockingBciTest.test_start_3x_acquire_stop " << endl;            
  FakeBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->start());
  boost::this_thread::sleep(boost::posix_time::seconds(1));
  BOOST_CHECK_EQUAL(1, fbci->mStartCount);
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());
  BOOST_CHECK(fbci->mAcquireRet <= bci->acquire());    
  boost::this_thread::sleep(boost::posix_time::seconds(10));
  BOOST_CHECK(1 <= fbci->mAcquireCount);
  BOOST_CHECK(bci->stop());
  BOOST_CHECK(bci->stop());
}

BOOST_AUTO_TEST_CASE(test_start_delete)
{
  cout << "NonblockingBciTest.test_start_delete " << endl;            
  IBci* fbci = new FakeBci();
  NonblockingBci* bci = new NonblockingBci(fbci);
  BOOST_CHECK(bci->start());
  delete bci;
}

BOOST_AUTO_TEST_SUITE_END()
