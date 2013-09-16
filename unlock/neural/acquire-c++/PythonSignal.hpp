#ifndef PYTHON_SIGNAL_HPP
#define PYTHON_SIGNAL_HPP

#include <boost/python.hpp>
#include <vector>
#include <stdint.h>
#include <cstddef>
#include <iostream>
#include <fstream>


#include "Portability.hpp"
#include "ISignal.hpp"
#include "ITimer.hpp"

class DllExport PythonSignal
{
 public:
  PythonSignal(ISignal* pSignal, ITimer* pTimer);
  virtual ~PythonSignal();
  bool open(/* boost::python::list mac */);
  bool init(size_t channels);
  size_t channels();
  bool start();
  size_t acquire();
  std::vector<int32_t> getdata(size_t samples);
  uint32_t elapsedMicroSecs();
  uint64_t timestamp();
  bool stop();
  bool close();
private:
    ISignal* mpSignal;
    ITimer* mpTimer;
    std::ofstream mReturnedDataLog;    
};

#endif
