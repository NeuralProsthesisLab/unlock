#include <boost/assert.hpp>
#include <algorithm>
#include <iostream>

#include "NonblockingSignal.hpp"
#include "AsyncSampleCollector.hpp"

using namespace std;
using namespace boost;
using namespace boost::lockfree;

NonblockingSignal::NonblockingSignal(ISignal* pSignal) : mpSignal(pSignal), mpProducerSamples(0), mpConsumerSamples(0), mpSampleRingBuffer(0), mpQueue(0), mpWorkController(0), mpAsyncSampleCollector(0) {
  BOOST_VERIFY(mpSignal != 0);
  // XXX - these should be injected
  mpProducerSamples = new Sample<uint32_t>[NonblockingSignal::SAMPLE_BUFFER_SIZE];
  mpConsumerSamples = new Sample<uint32_t>[NonblockingSignal::SAMPLE_BUFFER_SIZE];
  mpSampleRingBuffer = new SampleBuffer<uint32_t>();
  mpQueue = new spsc_queue<Sample<uint32_t>* > (NonblockingSignal::SAMPLE_BUFFER_SIZE-1);
  mpWorkController = new ManagedWorkController(false);
  BOOST_VERIFY(mpQueue != 0);
  BOOST_VERIFY(mpProducerSamples != 0);
  BOOST_VERIFY(mpConsumerSamples != 0);
  BOOST_VERIFY(mpSampleRingBuffer != 0);
  BOOST_VERIFY(mpWorkController != 0 && !mpWorkController->doWork());
}

NonblockingSignal::NonblockingSignal(const NonblockingSignal& copy)
  : mpSignal(copy.mpSignal), mpProducerSamples(copy.mpProducerSamples), mpConsumerSamples(copy.mpConsumerSamples),
    mpSampleRingBuffer(copy.mpSampleRingBuffer), mpQueue(copy.mpQueue), mpWorkController(copy.mpWorkController),
    mpAsyncSampleCollector(copy.mpAsyncSampleCollector)
{  
}

NonblockingSignal::~NonblockingSignal()  {
  BOOST_VERIFY(mpWorkController != 0);
  if (mpWorkController->doWork()) {
    waitForAsyncCollector();
  }
    
  if(mpAsyncSampleCollector != 0) {
    mpWorkController->setDoWorkState(false);
    mpAsyncSampleCollector->join();
    delete mpAsyncSampleCollector;
    mpAsyncSampleCollector = 0;
  }
  
  delete mpSignal;
  delete[] mpProducerSamples;
  delete[] mpConsumerSamples;
  delete mpSampleRingBuffer;
  delete mpQueue;
  delete mpWorkController;

  mpSignal=0;
  mpProducerSamples=0;
  mpConsumerSamples=0;
  mpSampleRingBuffer=0;
  mpQueue=0;
  mpWorkController=0;
}

NonblockingSignal& NonblockingSignal::operator=(const NonblockingSignal& other)
{
  mpSignal = other.mpSignal;
  mpProducerSamples = other.mpProducerSamples;
  mpConsumerSamples = other.mpConsumerSamples;
  mpSampleRingBuffer = other.mpSampleRingBuffer;
  mpQueue = other.mpQueue;
  mpWorkController = other.mpWorkController;
  mpAsyncSampleCollector = other.mpAsyncSampleCollector;
  return *this;
}

bool NonblockingSignal::open(uint8_t* pMacAddress) {
  BOOST_VERIFY(mpSignal != 0);
  BOOST_VERIFY(pMacAddress != 0);
  return mpSignal->open(pMacAddress);
}

bool NonblockingSignal::init(size_t channels) {
  BOOST_VERIFY(mpSignal != 0);
  return mpSignal->init(channels);
}

size_t NonblockingSignal::channels() {
  BOOST_VERIFY(mpSignal != 0);
  return mpSignal->channels();
}

bool NonblockingSignal::start()  {
  BOOST_VERIFY(mpSignal != 0);
  waitForAsyncCollector();
  bool ret = mpSignal->start();
  if(ret) {
    BOOST_VERIFY(mpAsyncSampleCollector == 0);
    mpWorkController->setDoWorkState(true);
    mpAsyncSampleCollector = new thread(AsyncSampleCollector(mpSignal, (boost::lockfree::spsc_queue<Sample<uint32_t>* >*)mpQueue,
							     mpWorkController, mpProducerSamples, NonblockingSignal::SAMPLE_BUFFER_SIZE, mpSampleRingBuffer));
  }
  return ret;
}

size_t NonblockingSignal::acquire()  {
  BOOST_VERIFY(mpWorkController != 0);
  BOOST_VERIFY(mpQueue != 0);
  
  if (!mpWorkController->doWork()) {
    // XXX - setup logging.  
    cerr << "NonblockingSignal.acquire: WARNING acquire called when device not started; returning 0"
         << endl; 
    return 0;
  }
  size_t count = 0;
  while(count < NonblockingSignal::SAMPLE_BUFFER_SIZE && mpQueue->pop(mpConsumerSamples+count)) {
    count++;
  }
  return count;
}

void NonblockingSignal::getdata(uint32_t* data, size_t n)  {
  BOOST_VERIFY(mpWorkController != 0);
  BOOST_VERIFY(mpConsumerSamples != 0);
  if (!mpWorkController->doWork()) {
    cerr << "NonblockingSignal.getdata: WARNING getdata called with " << data << ":"
         <<  n << " when device not started; not copying any data" << endl; 
    return;
  }
  
  for (int sample=0, pos=0; sample < n; sample++) {
    uint32_t* pSample = mpConsumerSamples[pos].sample();
    size_t length = mpConsumerSamples[pos].length();
    std::copy(pSample, pSample+length, data);
    data += length;
  }
}

uint64_t NonblockingSignal::timestamp()  {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->timestamp();
}

bool NonblockingSignal::stop()  {
  BOOST_VERIFY(mpSignal != 0);  
  waitForAsyncCollector();
  bool ret = mpSignal->stop();
  return ret;
}

bool NonblockingSignal::close()  {
  BOOST_VERIFY(mpSignal != 0);  
  return mpSignal->close();
}

void NonblockingSignal::waitForAsyncCollector() {
  BOOST_VERIFY(mpWorkController != 0);
  if(mpWorkController->doWork()) {
    mpWorkController->setDoWorkState(false);
  }
  
  if(mpAsyncSampleCollector != 0) {
    mpAsyncSampleCollector->join();
    delete mpAsyncSampleCollector;
    mpAsyncSampleCollector = 0;
  }
}
