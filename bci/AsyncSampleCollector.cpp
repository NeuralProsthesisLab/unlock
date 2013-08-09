#include <boost/assert.hpp>
#include <boost/thread.hpp>
#include <iostream>

#include "AsyncSampleCollector.hpp"

using namespace boost;
using namespace std;

AsyncSampleCollector::AsyncSampleCollector(Bci* pBci,
		       lockfree::spsc_queue<Sample<uint32_t>* >* pQueue,
		       atomic<bool>* pDone, Sample<uint32_t>* pSamples, SampleBuffer<uint32_t>* pRingBuffer) 
    : mpBci(pBci), mpQueue(pQueue), mpDone(pDone), mpSamples(pSamples), mpRingBuffer(pRingBuffer),
      mCurrentSample(0)
  {
    BOOST_VERIFY(mpBci != 0);
    BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
    BOOST_VERIFY(mpDone != 0);
    BOOST_VERIFY(mpSamples != 0);
    BOOST_VERIFY(mpRingBuffer != 0);
    cout << "Async collector created successfully " << (bool)*mpDone << endl;
  }

AsyncSampleCollector::AsyncSampleCollector(const AsyncSampleCollector& copy)
    : mpBci(copy.mpBci), mpQueue(copy.mpQueue), mpDone(copy.mpDone), mpSamples(copy.mpSamples),
      mpRingBuffer(copy.mpRingBuffer), mCurrentSample(copy.mCurrentSample) {
  }
    
    
AsyncSampleCollector::~AsyncSampleCollector() {
    mpSamples=0;
    mpRingBuffer=0;
    mpBci=0;
    mpDone=0;
    mpQueue=0;
 } 

AsyncSampleCollector& AsyncSampleCollector::operator=(const AsyncSampleCollector& other) {
    mpBci = other.mpBci;
    mpQueue = other.mpQueue;
    mpDone = other.mpDone;
    mpSamples = other.mpSamples;
    mpRingBuffer = other.mpRingBuffer;
    mCurrentSample = other.mCurrentSample;
    return *this;
  }
  
void AsyncSampleCollector::operator()() {
    cout << " mpDone = " << (bool)*mpDone << endl;
    BOOST_VERIFY(mpBci != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0);
    while(!(*(mpDone))) {
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