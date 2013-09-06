#include <boost/random/uniform_int_distribution.hpp>
#include <boost/assert.hpp>
#include <limits>
#include <iostream>

#include "PythonSignal.hpp"

PythonSignal::PythonSignal(ISignal* pSignal)
  : mpSignal(pSignal)
{
}

PythonSignal::~PythonSignal() {
  delete mpSignal;
}

bool PythonSignal::open(/* boost::python::list macAddress */) {
  uint8_t mac[6] = { 0x1, 0x2, 0x3, 0x4, 0x5, 0x6 };
  return mpSignal->open(mac);
}

bool PythonSignal::init(size_t channels) {
  return mpSignal->init(channels);
}

size_t PythonSignal::channels() {
    return mpSignal->channels();  
}

bool PythonSignal::start() {
    return mpSignal->start();  
}

size_t PythonSignal::acquire() {
    return mpSignal->acquire();
}

std::vector<uint32_t> PythonSignal::getdata(size_t samples) {
    std::vector<uint32_t> ret = std::vector<uint32_t>();
    if(samples == 0) {
      return ret;
    }
    
    try {
      uint32_t* buffer = new uint32_t[samples];
      BOOST_VERIFY(buffer != 0);
      mpSignal->getdata(buffer, samples);
      for (size_t i = 0; i < samples; i++) {
        ret.push_back(buffer[i]);
      }
      delete[] buffer;
      buffer = 0;
      return ret;
  } catch(...) {
    std::cerr << "PythonSignal.getdata: ERROR: exception raised; returning empty samples vector " << std::endl;
  }
  return ret;
}

uint64_t PythonSignal::timestamp() {
  return mpSignal->timestamp();
}

bool PythonSignal::stop() {
  return mpSignal->stop();
}

bool PythonSignal::close() {
  return mpSignal->close();
}

