#include <boost/python.hpp>

#include "nonblocking_bci.hpp"
#include "fake_bci.hpp"

using namespace boost::python;
/*
class NonblockingBCIWrapper : NonblockingBCI, wrapper<NonblockingBCI> {
};
*/

BCI* create_fake_bci() {
    return new FakeBCI();
}

BCI* create_enobio_bci() {
    return new FakeBCI();
}

BOOST_PYTHON_MODULE(boosted_bci)
{
    def("create_fake_bci", create_fake_bci, return_value_policy<manage_new_object>());
    def("create_enobio_bci", create_enobio_bci, return_value_policy<manage_new_object>());
    
    
    class_<NonblockingBCI, bases<BCI> >("NonblockingBCI", init<BCI*>())
        .def("open", &NonblockingBCI::open)
        .def("init", &NonblockingBCI::init)
        .def("start", &NonblockingBCI::start)    
        .def("acquire", &NonblockingBCI::acquire)
        .def("getdata", &NonblockingBCI::getdata)    
        .def("timestamp", &NonblockingBCI::timestamp)
        .def("stop", &NonblockingBCI::stop)    
        .def("close", &NonblockingBCI::close)             
        ;
}

