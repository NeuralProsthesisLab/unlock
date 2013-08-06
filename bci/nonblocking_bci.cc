#include "NonblockingBCI.hpp"
#include <iostream>
#include <boost/assert.hpp>

using namespace boost;
using namespace boost::lockfree;

static const size_t YIELD_THRESHOLD=1337;

class AsyncSampleCollector
{
public:
  AsyncSampleCollector(BCI* pBCI,
    lockfree::spsc_queue<Sample<uint32_t>*, lockfree::capacity<(SAMPLE_BUFFER_SIZE-1)> >* pQueue,
    atomic<bool>* pDone) 
    : mpBCI(pBCI), mpQueue(pQueue), mpDone(pDone), mpSamples(0), mpRingBuffer(0),
        mCurrentSample(0)
  {
    BOOST_VERIFY(mpBCI != 0);
    BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
    mpRingBuffer = new SampleBuffer<uint32_t>();
    mpSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
    BOOST_VERIFY(mpSamples != 0 && mpRingBuffer != 0);
  }

    AsyncSampleCollector(const AsyncSampleCollector& copy)
        : mpBCI(copy.mpBCI), mpQueue(copy.mpQueue), mpDone(copy.mpDone), mpSamples(copy.mpSamples),
            mpRingBuffer(copy.mpRingBuffer), mCurrentSample(copy.mCurrentSample) {
    }
    
    AsyncSampleCollector& operator=(const AsyncSampleCollector&) {
        
    }
    
  ~AsyncSampleCollector() {
    delete mpSamples;
    delete mpRingBuffer;
    mpSamples=0;
    mpBCI=0;
    mpQueue=0;
  }
  
  void operator()() {
    BOOST_VERIFY(mpBCI != 0 && mpQueue != 0 && mpSamples != 0 && mpRingBuffer != 0);
    while(!(*(mpDone))) {
      for(size_t i = 0; i < YIELD_THRESHOLD; i++) {
        size_t samples = mpBCI->acquire();
        uint32_t* pBuffer = mpRingBuffer->reserve(samples);
        mpBCI->getdata(pBuffer, samples);
        mpSamples[mCurrentSample].configure(pBuffer, samples);
        while (!mpQueue->push(mpSamples+mCurrentSample))
            ;
        mCurrentSample++;
      }
      thread::yield();
    }
  }

private:


private:
  BCI* mpBCI;
  spsc_queue<Sample<uint32_t>*, capacity<(SAMPLE_BUFFER_SIZE-1)> >* mpQueue;
  atomic<bool>* mpDone;
  Sample<uint32_t>* mpSamples;
  SampleBuffer<uint32_t>* mpRingBuffer;
  size_t mCurrentSample;
};


NonblockingBCI::NonblockingBCI(BCI* pBCI) : mpBCI(pBCI), mQueue(), mDone(false) {  
  mAsyncSampleCollector = thread(AsyncSampleCollector(mpBCI, &mQueue, &mDone));
}

NonblockingBCI::~NonblockingBCI()  {
  delete mpBCI;
}

bool NonblockingBCI::open(uint8_t mac_address[]) {
  return mpBCI->open(mac_address);
}

bool NonblockingBCI::init(size_t channels) {
  return mpBCI->init(channels);
}

bool NonblockingBCI::start()  {
  return mpBCI->start();
}

size_t NonblockingBCI::acquire()  {
/*    while (!done) {
        while (spsc_queue.pop(value))
            ++consumer_count;
    }

    while (spsc_queue.pop(value))
        ++consumer_count;    */
  // do some shit here...
  return 0;
}

void NonblockingBCI::getdata(uint32_t* data, size_t n)  {
  //  copy the data
}

uint64_t NonblockingBCI::timestamp()  {
  return mpBCI->timestamp();
}

bool NonblockingBCI::stop()  {
  return mpBCI->stop();

}

bool NonblockingBCI::close()  {
  mDone = true;
  return mpBCI->close();
}
