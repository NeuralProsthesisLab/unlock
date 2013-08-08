#include "nonblocking_bci.hpp"
#include <iostream>
#include <boost/assert.hpp>
#include <algorithm>

using namespace boost;
using namespace boost::lockfree;

static const size_t YIELD_THRESHOLD=1337;

#include <iostream>
using namespace std;

class AsyncSampleCollector
{
public:
  AsyncSampleCollector(BCI* pBCI,
		       lockfree::spsc_queue<Sample<uint32_t>*, lockfree::capacity<(SAMPLE_BUFFER_SIZE-1)> >* pQueue,
		       atomic<bool>* pDone, Sample<uint32_t>* pSamples, SampleBuffer<uint32_t>* pRingBuffer) 
    : mpBCI(pBCI), mpQueue(pQueue), mpDone(pDone), mpSamples(pSamples), mpRingBuffer(pRingBuffer),
      mCurrentSample(0)
  {
    BOOST_VERIFY(mpBCI != 0);
    BOOST_VERIFY(mpQueue != 0 && mpQueue->is_lock_free());
    BOOST_VERIFY(mpDone != 0);
    BOOST_VERIFY(mpSamples != 0);
    BOOST_VERIFY(mpRingBuffer != 0);
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
    mpSamples=0;
    mpRingBuffer=0;
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


NonblockingBCI::NonblockingBCI(BCI* pBCI) : mpBCI(pBCI), mpProducerSamples(0), mpConsumerSamples(0), mpSampleRingBuffer(0), mpQueue(0), mpDone(0) {
  BOOST_VERIFY(mpBCI != 0);
  mpProducerSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
  mpConsumerSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
  mpSampleRingBuffer = new SampleBuffer<uint32_t>();
  mpQueue = new spsc_queue<Sample<uint32_t>*, capacity<(SAMPLE_BUFFER_SIZE-1)> > ();
  mpDone = new atomic<bool>(true);
  BOOST_VERIFY(mpQueue != 0);
  BOOST_VERIFY(mpProducerSamples != 0);
  BOOST_VERIFY(mpConsumerSamples != 0);
  BOOST_VERIFY(mpSampleRingBuffer != 0);  
  BOOST_VERIFY(mpDone != 0 && *mpDone == true);
}

NonblockingBCI::NonblockingBCI(const NonblockingBCI& copy)
  : mpBCI(copy.mpBCI), mpProducerSamples(copy.mpProducerSamples), mpConsumerSamples(copy.mpConsumerSamples),
  mpSampleRingBuffer(copy.mpSampleRingBuffer), mpQueue(copy.mpQueue), mpDone(copy.mpDone),
  mpAsyncSampleCollector(copy.mpAsyncSampleCollector)
{  
}

NonblockingBCI::~NonblockingBCI()  {
  
  if (!(*mpDone)) {
    waitForAsyncCollector();
  }
  
  delete mpBCI;
  delete[] mpProducerSamples;
  delete[] mpConsumerSamples;
  delete mpSampleRingBuffer;
  delete mpQueue;
  delete mpDone;
  delete mpAsyncSampleCollector;
  mpBCI=0;
  mpProducerSamples=0;
  mpConsumerSamples=0;
  mpSampleRingBuffer=0;
  mpQueue=0;
  mpDone=0;
  mpAsyncSampleCollector=0;
}

NonblockingBCI& NonblockingBCI::operator=(const NonblockingBCI& other)
{
  mpBCI = other.mpBCI;
  mpProducerSamples = other.mpProducerSamples;
  mpConsumerSamples = other.mpConsumerSamples;
  mpSampleRingBuffer = other.mpSampleRingBuffer;
  mpQueue = other.mpQueue;
  mpDone = other.mpDone;
  mpAsyncSampleCollector = other.mpAsyncSampleCollector;
  return *this;
}

bool NonblockingBCI::open(uint8_t mac_address[]) {
  return mpBCI->open(mac_address);
}

bool NonblockingBCI::init(size_t channels) {
//  bool ret = mpBCI->init(channels);
  return mpBCI->init(channels);
}

bool NonblockingBCI::start()  {
  bool ret = mpBCI->start();
  if(ret) {
    *mpDone = false;
    mpAsyncSampleCollector = new thread(AsyncSampleCollector(mpBCI, mpQueue, mpDone, mpProducerSamples, mpSampleRingBuffer));
  }
  return ret;
}

size_t NonblockingBCI::acquire()  {
  if (*mpDone) {
    // XXX - setup logging.  
    cerr << "NonblockingBCI.acquire: WARNING acquire called when device not started; returning 0"
         << endl; 
    return 0;
  }
  
  size_t count = mpQueue->pop(&mpConsumerSamples, SAMPLE_BUFFER_SIZE);
  size_t acquired_size = 0;
  for (size_t sample = 0; sample < count; sample++) {
    acquired_size += (mpConsumerSamples[sample].length() * sizeof(uint32_t));
  }
  return acquired_size;
}

void NonblockingBCI::getdata(uint32_t* data, size_t n)  {
  if (*mpDone) {
    cerr << "NonblockingBCI.getdata: WARNING getdata called with " << data << ":"
         <<  n << " when device not started; not copying any data" << endl; 
    return;
  }
  
  for (int sample=0, pos=0; sample < n; sample++) {
    uint32_t* sample = mpConsumerSamples[pos].sample();
    size_t length = mpConsumerSamples[pos].length();
    std::copy(sample, sample+length, data);
    data += length;
  }
}

uint64_t NonblockingBCI::timestamp()  {
  return mpBCI->timestamp();
}

bool NonblockingBCI::stop()  {
  waitForAsyncCollector();
  return mpBCI->stop();
}

bool NonblockingBCI::close()  {
  return mpBCI->close();
}

void NonblockingBCI::waitForAsyncCollector() {
  if(!(*mpDone)) {
    *mpDone = true;
    mpAsyncSampleCollector->join();
  }
}