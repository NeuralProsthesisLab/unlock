#ifndef ASYNC_SAMPLE_COLLECTOR_HPP
#define ASYNC_SAMPLE_COLLECTOR_HPP

#include <boost/lockfree/spsc_queue.hpp>
#include <boost/atomic.hpp>
#include <cstddef>

#include "ISignal.hpp"
#include "Sample.hpp"
#include "SampleBuffer.hpp"
#include "IWorkController.hpp"
#include "Portability.hpp"

using namespace boost;
using namespace boost::lockfree;

class DllExport AsyncSampleCollector
{
 public:
  AsyncSampleCollector(ISignal* pSignal, lockfree::spsc_queue<Sample<uint32_t>* >* pQueue,
		       IWorkController* pWorkController, Sample<uint32_t>* pSamples,
		       size_t samplesSize, SampleBuffer<uint32_t>* pRingBuffer);
  AsyncSampleCollector(const AsyncSampleCollector& copy);
  virtual ~AsyncSampleCollector();
  
 public:
  size_t currentSample() const;
  void  incrementCurrentSample();

 public:
  AsyncSampleCollector& operator=(const AsyncSampleCollector& rhs);
  bool operator==(const AsyncSampleCollector& rhs) const;
  bool operator!=(const AsyncSampleCollector& rhs) const;  
  void operator()();
  
 private:
  ISignal* mpSignal;
  spsc_queue<Sample<uint32_t>* >* mpQueue;
  IWorkController* mpWorkController;
  Sample<uint32_t>* mpSamples;
  size_t mSamplesSize;
  size_t mCurrentSample;
  SampleBuffer<uint32_t>* mpRingBuffer;
};

#endif
