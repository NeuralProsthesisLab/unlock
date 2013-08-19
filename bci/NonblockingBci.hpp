#ifndef NONBLOCKING_BCI_HPP
#define NONBLOCKING_BCI_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/thread.hpp>
#include <boost/atomic.hpp>

#include "IBci.hpp"
#include "Sample.hpp"
#include "SampleBuffer.hpp"
#include "ManagedWorkController.hpp"
#include "Portability.hpp"

class DllExport NonblockingBci : public IBci
{
public:
    static const size_t SAMPLE_BUFFER_SIZE=8192;
    
public:
  NonblockingBci(IBci* pBci);
  NonblockingBci(const NonblockingBci& copy);
  virtual ~NonblockingBci();
  NonblockingBci& operator=(const NonblockingBci& other);
  
public:
  virtual bool open(uint8_t*);
  virtual bool init(size_t);
  virtual size_t channels();
  virtual bool start();
  virtual size_t acquire();
  virtual void getdata(uint32_t* data, size_t n);
  virtual uint64_t timestamp();
  virtual bool stop();
  virtual bool close();

private:
  void waitForAsyncCollector();
  
private:
  IBci* mpBci;
  Sample<uint32_t>* mpProducerSamples;
  Sample<uint32_t>* mpConsumerSamples;
  SampleBuffer<uint32_t>* mpSampleRingBuffer;
  boost::lockfree::spsc_queue<Sample<uint32_t>* >* mpQueue;
  boost::thread* mpAsyncSampleCollector;
  ManagedWorkController* mpWorkController;
};

#endif
