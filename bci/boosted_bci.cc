
#include <boost/python.hpp>
#include <stdint.h>

#include "bci.hpp"
#include "nonblocking_bci.hpp"
#include "fake_bci.hpp"


using namespace boost::python;
/*
class NonblockingBCIWrapper : NonblockingBCI, wrapper<NonblockingBCI> {
};
*/

class BCIPythonWrap : public BCI, public wrapper<BCI>
{
public:
    BCIPythonWrap(BCI* pBCI) : mpBCI(pBCI) {
        
    }
    
    virtual ~BCIPythonWrap() {
        delete mpBCI;
    }
    
    bool open(uint8_t mac[]) {
        return this->get_override("open")(mac);
    }
    
    bool init(size_t channels) {
        return this->get_override("init")(channels);
    }
    
    bool start() {
        return this->get_override("start")();        
    }
    
    size_t acquire() {
        return this->get_override("acquire")();                
        return 0;
    }
    
    void getdata(uint32_t* data, size_t n) {
        this->get_override("getdata")(data, n);        
    }
    
    uint64_t timestamp() {
        return this->get_override("timestamp")();                
        return 0;    
    }
    
    bool stop() {
        return this->get_override("stop")();                
    }
    
    bool close() {
        return this->get_override("close")();                
    }

private:
    BCI* mpBCI;    
};

BCI* create_fake_bci() {
    return new BCIPythonWrap(new FakeBCI());
}

BCI* create_enobio_bci() {
    return create_fake_bci();
}


BOOST_PYTHON_MODULE(boosted_bci)
{
    def("create_fake_bci", create_fake_bci, return_value_policy<manage_new_object>());
    def("create_enobio_bci", create_enobio_bci, return_value_policy<manage_new_object>());

    class_<BCIPythonWrap, boost::noncopyable>("BCI", no_init)
        .def("open", pure_virtual(&BCI::open))
        .def("init", pure_virtual(&BCI::init))
        .def("start", pure_virtual(&BCI::start))
        .def("acquire", pure_virtual(&BCI::acquire))
        .def("getdata", pure_virtual(&BCI::getdata))
        .def("timestamp", pure_virtual(&BCI::timestamp))
        .def("stop", pure_virtual(&BCI::stop))
        .def("close", pure_virtual(&BCI::close))                
    ;

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

