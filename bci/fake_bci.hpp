#ifndef FAKE_BCI_HPP
#define FAKE_BCI_HPP

#include "bci.hpp"

class FakeBCI : public BCI {
public:
  FakeBCI();
  virtual ~FakeBCI();
  virtual bool open(uint8_t[]);
  virtual bool init(size_t);
  virtual bool start();
  virtual size_t acquire();
  virtual void getdata(uint32_t* data, size_t n);
  virtual uint64_t timestamp();
  virtual bool stop();
  virtual bool close();		
};

#endif
