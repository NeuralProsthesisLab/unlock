#ifndef IBCI_HPP
#define IBCI_HPP

#include <stdint.h>
#include <cstddef>

#include "Portability.hpp"

class DllExport IBci
{
public:
  virtual ~IBci() {}
  virtual bool open(uint8_t* mac)=0;
  virtual bool init(size_t channels)=0;
  virtual size_t channels()=0;
  virtual bool start()=0;
  virtual size_t acquire()=0;
  virtual void getdata(uint32_t* buffer, size_t samples)=0;
  virtual uint64_t timestamp()=0;
  virtual bool stop()=0;
  virtual bool close()=0;		
};

#endif
