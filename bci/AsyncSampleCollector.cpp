#include <boost/assert.hpp>
#include <boost/thread.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"

using namespace boost;
using namespace std;

static const size_t YIELD_THRESHOLD=512;

AsyncSampleCollector::AsyncSampleCollector(IBci* pBci,
		       lockfree::spsc_queue<Sample<uint32_t>* >* pQueue,
		       IWorkController* pWorkController, Sample<uint32_t>* pSamples, size_t samplesSize, SampleBuffer<uint32_t>* pRingBuffer) 
    : mpBci(pBci), mpQueue(pQueue), mpWorkController(pWorkController), mpSamples(pSamples), mSamplesSize(samplesSize),
      mpRingBuffer(pRingBuffer), mCurrentSample(0)
  {
    BOOST_VERIFY(mpBci != 0);
    BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
    BOOST_VERIFY(mpWorkController != 0);
    BOOST_VERIFY(mpSamples != 0);
    BOOST_VERIFY(mSamplesSize > 0);
    BOOST_VERIFY(mpRingBuffer != 0);
  }

AsyncSampleCollector::AsyncSampleCollector(const AsyncSampleCollector& copy)
    : mpBci(copy.mpBci), mpQueue(copy.mpQueue), mpWorkController(copy.mpWorkController), mpSamples(copy.mpSamples),
      mSamplesSize(copy.mSamplesSize), mCurrentSample(copy.mCurrentSample), mpRingBuffer(copy.mpRingBuffer){
  }
    
    
AsyncSampleCollector::~AsyncSampleCollector() {
    mpSamples=0;
    mpRingBuffer=0;
    mpBci=0;
    mpWorkController=0;
    mpQueue=0;
    
 } 

size_t AsyncSampleCollector::currentSample() const {
  return mCurrentSample;
}

void  AsyncSampleCollector::incrementCurrentSample() {
  BOOST_VERIFY(mCurrentSample <= mSamplesSize);
  mCurrentSample++;
  if (mCurrentSample == mSamplesSize) {
    mCurrentSample = 0;
  }
}  

AsyncSampleCollector& AsyncSampleCollector::operator=(const AsyncSampleCollector& rhs) {
    mpBci = rhs.mpBci;
    mpQueue = rhs.mpQueue;
    mpWorkController = rhs.mpWorkController;
    mpSamples = rhs.mpSamples;
    mSamplesSize = rhs.mSamplesSize;
    mCurrentSample = rhs.mCurrentSample;
    mpRingBuffer = rhs.mpRingBuffer;
    return *this;
  }
  
bool AsyncSampleCollector::operator==(const AsyncSampleCollector& rhs) const {
    if (mpBci == rhs.mpBci && mpQueue == rhs.mpQueue && mpWorkController == rhs.mpWorkController
        && mpSamples == rhs.mpSamples && mpRingBuffer == rhs.mpRingBuffer
        && mCurrentSample == rhs.mCurrentSample) {
      return true;
    } else {
      return false;
    }
  }
  
bool AsyncSampleCollector::operator!=(const AsyncSampleCollector& rhs) const {
  return !(*this == rhs);
}
  
void AsyncSampleCollector::operator()() {
    BOOST_VERIFY(mpBci != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0 && mpWorkController != 0);
    size_t iterations = 0;
    while(mpWorkController->doWork()) {
      BOOST_VERIFY(mpBci != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0 && mpWorkController != 0);      
      iterations++;
      if (iterations == YIELD_THRESHOLD) {
        iterations = 0;
        thread::yield();
      }
      size_t samples = mpBci->acquire();
      size_t channels = mpBci->channels();
      uint32_t* pBuffer = mpRingBuffer->reserve(samples*channels);
      mpBci->getdata(pBuffer, samples);
      mpSamples[mCurrentSample].configure(pBuffer, samples*channels);
      
      while (!mpQueue->push(mpSamples+mCurrentSample)) {
        if (!mpWorkController->doWork()) {
          cerr << "AsyncSampleCollector.operator()(): WARNING stopping work with a full queue" << endl;
          break;
        }
      }
      
      incrementCurrentSample();
    }
}
   