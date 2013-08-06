#include "nonblocking_bci.hpp"
#include <iostream>
#include <boost/assert.hpp>
#include <algorithm>

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
    
  AsyncSampleCollector& operator=(const AsyncSampleCollector& other) {
    mpBCI = other.mpBCI;
    mpQueue = other.mpQueue;
    mpDone = other.mpDone;
    mpSamples = other.mpSamples;
    mpRingBuffer = other.mpRingBuffer;
    mCurrentSample = other.mCurrentSample;
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
  BCI* mpBCI;
  spsc_queue<Sample<uint32_t>*, capacity<(SAMPLE_BUFFER_SIZE-1)> >* mpQueue;
  atomic<bool>* mpDone;
  Sample<uint32_t>* mpSamples;
  SampleBuffer<uint32_t>* mpRingBuffer;
  size_t mCurrentSample;
};


NonblockingBCI::NonblockingBCI(BCI* pBCI) : mpBCI(pBCI), mpSamples(0), mpQueue(0), mpDone(0) {  
  mpSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
  mpQueue = new spsc_queue<Sample<uint32_t>*, capacity<(SAMPLE_BUFFER_SIZE-1)> > ();
  mpDone = new atomic<bool>();
  mpAsyncSampleCollector = new thread(AsyncSampleCollector(mpBCI, mpQueue, mpDone));  
}

NonblockingBCI::NonblockingBCI(const NonblockingBCI& copy)
  : mpBCI(copy.mpBCI), mpSamples(copy.mpSamples), mpQueue(copy.mpQueue), mpDone(copy.mpDone),
  mpAsyncSampleCollector(copy.mpAsyncSampleCollector)
{  
}

NonblockingBCI::~NonblockingBCI()  {
  delete mpBCI;
  delete mpSamples;
  delete mpQueue;
  delete mpDone;
  delete mpAsyncSampleCollector;
  mpBCI=0;
  mpSamples=0;
}

NonblockingBCI& NonblockingBCI::operator=(const NonblockingBCI& other)
{
  mpBCI = other.mpBCI;
  mpSamples = other.mpSamples;
  mpQueue = other.mpQueue;
  mpDone = other.mpDone;
  mpAsyncSampleCollector = other.mpAsyncSampleCollector;
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
  size_t count = mpQueue->pop(&mpSamples, SAMPLE_BUFFER_SIZE);
  size_t acquired_size = 0;
  for (size_t sample = 0; sample < count; sample++) {
    acquired_size += (mpSamples[sample].length() * sizeof(uint32_t));
  }
  return acquired_size;
}

void NonblockingBCI::getdata(uint32_t* data, size_t n)  {
  for (int sample=0, pos=0; sample < n; sample++) {
    uint32_t* sample = mpSamples[pos].sample();
    size_t length = mpSamples[pos].length();
    std::copy(sample, sample+length, data);
    data += length;
  }
}

uint64_t NonblockingBCI::timestamp()  {
  return mpBCI->timestamp();
}

bool NonblockingBCI::stop()  {
  return mpBCI->stop();

}

bool NonblockingBCI::close()  {
  *(mpDone) = true;
//  mpAsyncSampleCollector.join();
  return mpBCI->close();
}
