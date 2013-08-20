
#include "ISignal.hpp"
#include "FakeSignal.hpp"
#include "NonblockingSignal.hpp"
#include "Portability.hpp"

#include <boost/python.hpp>
#include <stdint.h>

using namespace boost::python;

class DllExport SignalPythonWrap : public ISignal, public wrapper<ISignal>
{
 public:
  SignalPythonWrap(ISignal* pSignal) : mpSignal(pSignal) {
        
  }
    
  virtual ~SignalPythonWrap() {
    delete mpSignal;
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
  ISignal* mpSignal;    
};

ISignal* create_fake_bci() {
  return new FakeSignal(); 
}

ISignal* create_enobio_bci() {
  return create_fake_bci();
}

BOOST_PYTHON_MODULE(signal)
{
  def("create_fake_signal", create_fake_bci, return_value_policy<manage_new_object>());
  def("create_enobio_signal", create_enobio_bci, return_value_policy<manage_new_object>());

  class_<SignalPythonWrap, boost::noncopyable>("ISignal", no_init)
    .def("open", pure_virtual(&ISignal::open))
    .def("init", pure_virtual(&ISignal::init))
    .def("channels", pure_virtual(&ISignal::channels))      
    .def("start", pure_virtual(&ISignal::start))
    .def("acquire", pure_virtual(&ISignal::acquire))
    .def("getdata", pure_virtual(&ISignal::getdata))
    .def("timestamp", pure_virtual(&ISignal::timestamp))
    .def("stop", pure_virtual(&ISignal::stop))
    .def("close", pure_virtual(&ISignal::close))             
    ;

  class_<NonblockingSignal, bases<ISignal> >("NonblockingSignal", init<ISignal*>())
    .def("open", &NonblockingSignal::open)
    .def("init", &NonblockingSignal::init)
    .def("channels", &NonblockingSignal::channels)        
    .def("start", &NonblockingSignal::start)    
    .def("acquire", &NonblockingSignal::acquire)
    .def("getdata", &NonblockingSignal::getdata)    
    .def("timestamp", &NonblockingSignal::timestamp)
    .def("stop", &NonblockingSignal::stop)    
    .def("close", &NonblockingSignal::close)             
    ;
}

