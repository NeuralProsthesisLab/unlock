#include <boost/random/uniform_int_distribution.hpp>
#include <boost/assert.hpp>
#include <limits>

using namespace std;

#include "PythonSignal.hpp"

PythonSignal::PythonSignal(ISignal* pSignal, ITimer* pTimer)
  : mpSignal(pSignal), mpTimer(pTimer)
{
    BOOST_VERIFY(mpSignal != 0 && mpTimer != 0);
    mReturnedDataLog.open("PythonSignalLog.txt");
}

PythonSignal::~PythonSignal() {
  BOOST_VERIFY(mpSignal != 0);  
  delete mpSignal;
  mReturnedDataLog.close();
}

bool PythonSignal::open(boost::python::list macAddress) {
  BOOST_VERIFY(mpSignal != 0);
  uint8_t mac[6] = {0,0,0,0,0,0};  
  if(boost::python::extract<size_t>(macAddress.attr("__len__")()) >= 6) {
    for (int i = 5; i >= 0; i--) {
      mac[i] = boost::python::extract<uint8_t>(macAddress.pop());
    }
  }
  return mpSignal->open(mac);
}

bool PythonSignal::init(size_t channels) {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->init(channels);
}

size_t PythonSignal::channels() {
  BOOST_VERIFY(mpSignal != 0);
    return mpSignal->channels();  
}

bool PythonSignal::start() {
  BOOST_VERIFY(mpSignal != 0);  
    return mpSignal->start();  
}

size_t PythonSignal::acquire() {
  BOOST_VERIFY(mpSignal != 0);
  try {
    return mpSignal->acquire();
  } catch(...) {
    std::cerr << "PythonSignal.acquire: ERROR exception raised; returning 0 samples" << std::endl;
    return 0;
  }
}

std::vector<int32_t> PythonSignal::getdata(size_t samples) {
  BOOST_VERIFY(mpSignal != 0);
    std::vector<int32_t> ret = std::vector<int32_t>();
    if(samples == 0) {
      return ret;
    }
    
    try {
      uint32_t* buffer = new uint32_t[samples];
      BOOST_VERIFY(buffer != 0);
      mpSignal->getdata(buffer, samples);
      for (size_t i = 0; i < samples; i++) {
        ret.push_back((int32_t)buffer[i]);
        mReturnedDataLog << (int32_t) ret.back() << " ";
        if((i+1) % mpSignal->channels() == 0) {
          mReturnedDataLog << endl;
        }

      }
      delete[] buffer;
      buffer = 0;
      return ret;
  } catch(...) {
    std::cerr << "PythonSignal.getdata: ERROR: exception raised; returning empty samples vector " << std::endl;
  }
  return ret;
}

uint32_t PythonSignal::elapsedMicroSecs() {
  return mpTimer->elapsedMicroSecs();
}

uint64_t PythonSignal::timestamp() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->timestamp();
}

bool PythonSignal::stop() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->stop();
}

bool PythonSignal::close() {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->close();
}

