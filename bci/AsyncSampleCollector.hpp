#ifndef ASYNC_SAMPLE_COLLECTOR_HPP
#define ASYNC_SAMPLE_COLLECTOR_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/atomic.hpp>
#include <cstddef>

#include "IBci.hpp"
#include "Sample.hpp"
#include "SampleBuffer.hpp"
#include "IWorkController.hpp"

using namespace boost;
using namespace boost::lockfree;

class AsyncSampleCollector
{
public:
  static const size_t YIELD_THRESHOLD=1337;
  
public:
  AsyncSampleCollector(IBci* pBci, lockfree::spsc_queue<Sample<uint32_t>* >* pQueue,
		       IWorkController* pWorkController, Sample<uint32_t>* pSamples, SampleBuffer<uint32_t>* pRingBuffer);
  
  AsyncSampleCollector(const AsyncSampleCollector& copy);
  virtual ~AsyncSampleCollector();
  
public:
  AsyncSampleCollector& operator=(const AsyncSampleCollector& other);
  void operator()();
  
private:
  IBci* mpBci;
  spsc_queue<Sample<uint32_t>* >* mpQueue;
  IWorkController* mpWorkController;
  Sample<uint32_t>* mpSamples;
  SampleBuffer<uint32_t>* mpRingBuffer;
  size_t mCurrentSample;
};

#endif