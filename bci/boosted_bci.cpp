
#include "IBci.hpp"
#include "FakeBci.hpp"
#include "NonblockingBci.hpp"
#include "Portability.hpp"

#include <boost/python.hpp>
#include <stdint.h>

using namespace boost::python;

class DllExport BciPythonWrap : public IBci, public wrapper<IBci>
{
 public:
  BciPythonWrap(IBci* pBci) : mpBci(pBci) {
        
  }
    
  virtual ~BciPythonWrap() {
    delete mpBci;
  }
    
  bool open(uint8_t mac[]) {
    return this->get_override("open")(mac);
  }
    
  bool init(size_t channels) {
    return this->get_override("init")(channels);
  }
    
  size_t channels() {
    return this->get_override("channels")();
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
  IBci* mpBci;    
};

IBci* create_fake_bci() {
  return new FakeBci(); 
}

IBci* create_enobio_bci() {
  return create_fake_bci();
}

BOOST_PYTHON_MODULE(boosted_bci)
{
  def("create_fake_bci", create_fake_bci, return_value_policy<manage_new_object>());
  def("create_enobio_bci", create_enobio_bci, return_value_policy<manage_new_object>());

  class_<BciPythonWrap, boost::noncopyable>("Bci", no_init)
    .def("open", pure_virtual(&IBci::open))
    .def("init", pure_virtual(&IBci::init))
    .def("channels", pure_virtual(&IBci::channels))      
    .def("start", pure_virtual(&IBci::start))
    .def("acquire", pure_virtual(&IBci::acquire))
    .def("getdata", pure_virtual(&IBci::getdata))
    .def("timestamp", pure_virtual(&IBci::timestamp))
    .def("stop", pure_virtual(&IBci::stop))
    .def("close", pure_virtual(&IBci::close))             
    ;

  class_<NonblockingBci, bases<IBci> >("NonblockingBci", init<IBci*>())
    .def("open", &NonblockingBci::open)
    .def("init", &NonblockingBci::init)
    .def("channels", &NonblockingBci::channels)        
    .def("start", &NonblockingBci::start)    
    .def("acquire", &NonblockingBci::acquire)
    .def("getdata", &NonblockingBci::getdata)    
    .def("timestamp", &NonblockingBci::timestamp)
    .def("stop", &NonblockingBci::stop)    
    .def("close", &NonblockingBci::close)             
    ;
}

