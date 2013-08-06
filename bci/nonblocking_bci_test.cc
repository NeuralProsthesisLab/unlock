
#define BOOST_TEST_MODULE NonblockingBCITest
#include <boost/test/included/unit_test.hpp>
#include "nonblocking_bci.hpp"
//#include <boost/test/unit_test.hpp>

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
 
BOOST_AUTO_TEST_CASE(test)
{
    int e = 32;
    int c = 4;
    BOOST_TEST_MESSAGE(m);
    
    BOOST_CHECK(e == m * c * c);
}
 
BOOST_AUTO_TEST_CASE(test1)
{
    int f = 10;
    int a = 5;
 
    BOOST_CHECK(f == m * a);
}
 
BOOST_AUTO_TEST_SUITE_END()
