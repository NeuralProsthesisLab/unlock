#include "Enobio3G.h"
#include "ISignal.hpp"
#include "RandomSignal.hpp"
#include "NonblockingSignal.hpp"
#include "Portability.hpp"
#include "PythonSignal.hpp"
#include "EnobioSignalHandler.hpp"
#include "EnobioDataReceiver.hpp"
#include "EnobioStatusReceiver.hpp"
#include "ITimer.hpp"
#include "WinTimer.hpp"

#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <vector>
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

class DllExport TimerPythonWrap : public ITimer, public wrapper<ITimer>
{
 public:
  TimerPythonWrap(ITimer* pTimer) : mpTimer(pTimer) {
  }
    
  virtual ~TimerPythonWrap() {
    delete mpTimer;
  }
  
  void start() {
    this->get_override("start")();
  }

  uint32_t elapsedCycles() {
    return this->get_override("elapsedCycles")();    
  }
  
  uint32_t elapsedMilliSecs() {
    return this->get_override("elapsedMilliSecs")();    
  }
  
  uint32_t elapsedMicroSecs() {
    return this->get_override("elapsedMicroSecs")();    
  }
  
  int64_t getFrequency() {
    return this->get_override("getFrequency")();
  }
  
  int64_t getStartValue() {
    return this->get_override("getStartValue")();
  }
  
 private:
  ITimer* mpTimer;    
};

ITimer* create_timer() {
  ITimer* pTimer = new WinTimer();
  pTimer->start();
  return pTimer;
}

PythonSignal* create_random_signal(ITimer* pTimer) {
  ISignal* pSignal = new RandomSignal();
  PythonSignal* pPythonSignal = new PythonSignal(pSignal, pTimer);
  return pPythonSignal;  
}

PythonSignal* create_enobio_signal(ITimer* pTimer) {

  Enobio3G* pEnobio3G = new Enobio3G();
  EnobioSignalHandler* pEnobioSignalHandler = new EnobioSignalHandler(pEnobio3G, pTimer);
  
  EnobioDataReceiver* pDataReceiver = new EnobioDataReceiver(pEnobioSignalHandler);
  pEnobioSignalHandler->setEnobioDataReceiver(pDataReceiver);
  
  EnobioStatusReceiver* pStatusReceiver = new EnobioStatusReceiver(pEnobioSignalHandler);
  pEnobioSignalHandler->setEnobioStatusReceiver(pStatusReceiver);

  NonblockingSignal* pNonblockingSignal = new NonblockingSignal(pEnobioSignalHandler);
  PythonSignal* pPythonSignal = new PythonSignal(pNonblockingSignal, pTimer);
  
  return pPythonSignal;
}

BOOST_PYTHON_MODULE(neuralsignal)
{
  class_<std::vector<int32_t> >("int32_vector")
        .def(vector_indexing_suite<std::vector<int32_t> >() );
        
  def("create_timer", create_timer, return_value_policy<manage_new_object>());
  def("create_random_signal", create_random_signal, return_value_policy<manage_new_object>());
  def("create_enobio_signal", create_enobio_signal, return_value_policy<manage_new_object>());

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

  class_<TimerPythonWrap, boost::noncopyable>("ITimer", no_init)
    .def("start", pure_virtual(&ITimer::start))
    .def("elapsedCycles", pure_virtual(&ITimer::elapsedCycles))
    .def("elapsedMilliSecs", pure_virtual(&ITimer::elapsedMilliSecs))
    .def("elapsedMicroSecs", pure_virtual(&ITimer::elapsedMicroSecs))
    .def("getFrequency", pure_virtual(&ITimer::getFrequency))
    .def("getStartValue", pure_virtual(&ITimer::getStartValue))
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
    
  class_<PythonSignal>("PythonSignal", init<ISignal*, ITimer*>())
    .def("open", &PythonSignal::open)
    .def("init", &PythonSignal::init)
    .def("channels", &PythonSignal::channels)        
    .def("start", &PythonSignal::start)    
    .def("acquire", &PythonSignal::acquire)
    .def("getdata", &PythonSignal::getdata)
    .def("elapsedMicroSecs", &PythonSignal::elapsedMicroSecs)
    .def("timestamp", &PythonSignal::timestamp)
    .def("stop", &PythonSignal::stop)    
    .def("close", &PythonSignal::close)             
    ;
}

