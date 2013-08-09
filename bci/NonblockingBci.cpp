#include <boost/assert.hpp>
#include <algorithm>
#include <iostream>

#include "NonblockingBci.hpp"
#include "AsyncSampleCollector.hpp"

using namespace std;
using namespace boost;
using namespace boost::lockfree;

NonblockingBci::NonblockingBci(IBci* pBci) : mpBci(pBci), mpProducerSamples(0), mpConsumerSamples(0), mpSampleRingBuffer(0), mpQueue(0), mpWorkController(0) {
  BOOST_VERIFY(mpBci != 0);
  mpProducerSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
  mpConsumerSamples = new Sample<uint32_t>[SAMPLE_BUFFER_SIZE];
  mpSampleRingBuffer = new SampleBuffer<uint32_t>();
  mpQueue = new spsc_queue<Sample<uint32_t>*, capacity<(SAMPLE_BUFFER_SIZE-1)> > ();
  mpWorkController = new ManagedWorkController(false);
  BOOST_VERIFY(mpQueue != 0);
  BOOST_VERIFY(mpProducerSamples != 0);
  BOOST_VERIFY(mpConsumerSamples != 0);
  BOOST_VERIFY(mpSampleRingBuffer != 0);
  BOOST_VERIFY(mpWorkController != 0 && !mpWorkController->doWork());
}

NonblockingBci::NonblockingBci(const NonblockingBci& copy)
  : mpBci(copy.mpBci), mpProducerSamples(copy.mpProducerSamples), mpConsumerSamples(copy.mpConsumerSamples),
  mpSampleRingBuffer(copy.mpSampleRingBuffer), mpQueue(copy.mpQueue), mpWorkController(copy.mpWorkController),
  mpAsyncSampleCollector(copy.mpAsyncSampleCollector)
{  
}

NonblockingBci::~NonblockingBci()  {
  BOOST_VERIFY(mpWorkController != 0);
  if (mpWorkController->doWork()) {
    waitForAsyncCollector();
  }
  
  delete mpBci;
  delete[] mpProducerSamples;
  delete[] mpConsumerSamples;
  delete mpSampleRingBuffer;
  delete mpQueue;
  delete mpWorkController;
  if(mpAsyncSampleCollector != 0) {
    delete mpAsyncSampleCollector;
    mpAsyncSampleCollector = 0;
  }
  mpBci=0;
  mpProducerSamples=0;
  mpConsumerSamples=0;
  mpSampleRingBuffer=0;
  mpQueue=0;
  mpWorkController=0;
}

NonblockingBci& NonblockingBci::operator=(const NonblockingBci& other)
{
  mpBci = other.mpBci;
  mpProducerSamples = other.mpProducerSamples;
  mpConsumerSamples = other.mpConsumerSamples;
  mpSampleRingBuffer = other.mpSampleRingBuffer;
  mpQueue = other.mpQueue;
  mpWorkController = other.mpWorkController;
  mpAsyncSampleCollector = other.mpAsyncSampleCollector;
  return *this;
}

bool NonblockingBci::open(uint8_t mac_address[]) {
  return mpBci->open(mac_address);
}

bool NonblockingBci::init(size_t channels) {
  return mpBci->init(channels);
}

size_t NonblockingBci::channels() {
  return mpBci->channels();
}

bool NonblockingBci::start()  {
  waitForAsyncCollector();
  bool ret = mpBci->start();
  if(ret) {
    cerr << "Starting... " << endl;
    BOOST_VERIFY(mpAsyncSampleCollector == 0);
    mpWorkController->setDoWorkState(true);
    mpAsyncSampleCollector = new thread(AsyncSampleCollector(mpBci, (boost::lockfree::spsc_queue<Sample<uint32_t>* >*)mpQueue, mpWorkController, mpProducerSamples, mpSampleRingBuffer));
  }
  return ret;
}

size_t NonblockingBci::acquire()  {
  if (!mpWorkController->doWork()) {
    // XXX - setup logging.  
    cerr << "NonblockingBci.acquire: WARNING acquire called when device not started; returning 0"
         << endl; 
    return 0;
  }
  
  size_t count = mpQueue->pop(&mpConsumerSamples, SAMPLE_BUFFER_SIZE);
/*  size_t acquired_size = 0;
  for (size_t sample = 0; sample < count; sample++) {
    acquired_size += (mpConsumerSamples[sample].length() * sizeof(uint32_t));
  }
  */
  cout << "count = " << count << endl;
  return count;
}

void NonblockingBci::getdata(uint32_t* data, size_t n)  {
  if (!mpWorkController->doWork()) {
    cerr << "NonblockingBci.getdata: WARNING getdata called with " << data << ":"
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

uint64_t NonblockingBci::timestamp()  {
  return mpBci->timestamp();
}

bool NonblockingBci::stop()  {
  waitForAsyncCollector();
  return mpBci->stop();
}

bool NonblockingBci::close()  {
  return mpBci->close();
}

void NonblockingBci::waitForAsyncCollector() {
  if(mpWorkController->doWork()) {
    BOOST_VERIFY(mpAsyncSampleCollector != 0);
    mpWorkController->setDoWorkState(false);
    mpAsyncSampleCollector->join();
    delete mpAsyncSampleCollector;
    mpAsyncSampleCollector = 0;
  }
}