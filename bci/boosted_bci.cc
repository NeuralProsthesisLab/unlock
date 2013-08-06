#include <boost/python.hpp>

#include "NonblockingBCI.hpp"
#include "SampleBuffer.hpp"

char const* greet() {
    return "Hello, world";
}

BOOST_PYTHON_MODULE(boosted_bci)
{
    using namespace boost::python;
    def("greet", greet);
}
