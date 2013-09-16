#include <boost/test/unit_test.hpp>
#include "Logger.hpp"

using namespace std;

BOOST_AUTO_TEST_SUITE(LoggerTest)

BOOST_AUTO_TEST_CASE(test_logger)
{
  cout << "LoggerTest.test_logger " << endl;
  Logger log("My logger");
  log.debug("DEBUG");
  log.info("WARN");  
  log.warn("WARN");
  log.error("ERROR");
  log.fatal("FATAL");
}

BOOST_AUTO_TEST_SUITE_END()
