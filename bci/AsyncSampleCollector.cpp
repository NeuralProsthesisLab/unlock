#include <boost/assert.hpp>
#include <boost/thread.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"

using namespace boost;
using namespace std;

AsyncSampleCollector::AsyncSampleCollector(IBci* pBci,
		       lockfree::spsc_queue<Sample<uint32_t>* >* pQueue,
		       IWorkController* pWorkController, Sample<uint32_t>* pSamples, SampleBuffer<uint32_t>* pRingBuffer) 
    : mpBci(pBci), mpQueue(pQueue), mpWorkController(pWorkController), mpSamples(pSamples), mpRingBuffer(pRingBuffer),
      mCurrentSample(0)
  {
    BOOST_VERIFY(mpBci != 0);
    BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
    BOOST_VERIFY(mpWorkController != 0);
    BOOST_VERIFY(mpSamples != 0);
    BOOST_VERIFY(mpRingBuffer != 0);
    cout << "Async collector created successfully " << mpWorkController->doWork() << endl;
  }

AsyncSampleCollector::AsyncSampleCollector(const AsyncSampleCollector& copy)
    : mpBci(copy.mpBci), mpQueue(copy.mpQueue), mpWorkController(copy.mpWorkController), mpSamples(copy.mpSamples),
      mpRingBuffer(copy.mpRingBuffer), mCurrentSample(copy.mCurrentSample) {
  }
    
    
AsyncSampleCollector::~AsyncSampleCollector() {
    mpSamples=0;
    mpRingBuffer=0;
    mpBci=0;
    mpWorkController=0;
    mpQueue=0;
 } 

AsyncSampleCollector& AsyncSampleCollector::operator=(const AsyncSampleCollector& rhs) {
    mpBci = rhs.mpBci;
    mpQueue = rhs.mpQueue;
    mpWorkController = rhs.mpWorkController;
    mpSamples = rhs.mpSamples;
    mpRingBuffer = rhs.mpRingBuffer;
    mCurrentSample = rhs.mCurrentSample;
    return *this;
  }
  
bool AsyncSampleCollector::operator==(const AsyncSampleCollector& rhs) {
    if (mpBci == rhs.mpBci && mpQueue == rhs.mpQueue && mpWorkController == rhs.mpWorkController
        && mpSamples == rhs.mpSamples && mpRingBuffer == rhs.mpRingBuffer
        && mCurrentSample == rhs.mCurrentSample) {
      return true;
    } else {
      return false;
    }
  }
  
void AsyncSampleCollector::operator()() {
    BOOST_VERIFY(mpBci != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0 && mpWorkController != 0);
    cout << " mpDone = " << mpWorkController->doWork() << endl;
    
    while(mpWorkController->doWork()) {
      for(size_t i = 0; i < YIELD_THRESHOLD; i++) {
        size_t samples = mpBci->acquire();
        size_t channels = mpBci->channels();
        uint32_t* pBuffer = mpRingBuffer->reserve(samples*channels);
        mpBci->getdata(pBuffer, samples);
        mpSamples[mCurrentSample].configure(pBuffer, samples);
        while (!mpQueue->push(mpSamples+mCurrentSample))
          ;
        mCurrentSample++;
      }
      thread::yield();
    }
  }