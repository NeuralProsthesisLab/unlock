#ifndef NONBLOCKING_BCI_HPP
#define NONBLOCKING_BCI_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/thread.hpp>
#include <boost/atomic.hpp>

#include "bci.hpp"
#include "sample.hpp"

static const size_t SAMPLE_BUFFER_SIZE=8192;

class NonblockingBCI : public BCI {
public:
  NonblockingBCI(BCI*);
  virtual ~NonblockingBCI();
  virtual bool open(uint8_t[]);
  virtual bool init(size_t);
  virtual bool start();
  virtual size_t acquire();
  virtual void getdata(uint32_t* data, size_t n);
  virtual uint64_t timestamp();
  virtual bool stop();
  virtual bool close();
private:
  BCI* mpBCI;
  Sample<uint32_t>* mpSamples;
  boost::lockfree::spsc_queue<Sample<uint32_t>*, boost::lockfree::capacity<(SAMPLE_BUFFER_SIZE-1)> > mQueue;
  boost::thread mAsyncSampleCollector;
  boost::atomic<bool> mDone;

};

#endif
