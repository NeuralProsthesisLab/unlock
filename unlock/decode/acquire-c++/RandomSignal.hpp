#ifndef RANDOM_SIGNAL_HPP
#define RANDOM_SIGNAL_HPP

#include <boost/random/mersenne_twister.hpp>

#include "ISignal.hpp"
#include "Portability.hpp"

class DllExport RandomSignal : public ISignal
{
 public:
  static const size_t MAC_ADDRESS_SIZE=6;    

 public:
  RandomSignal();
  virtual ~RandomSignal();
  virtual bool open(uint8_t* mac);
  virtual bool init(size_t channels);
  virtual size_t channels();
  virtual bool start();
  virtual size_t acquire();
  virtual void getdata(uint32_t* buffer, size_t samples);
  virtual uint64_t timestamp();
  virtual bool stop();
  virtual bool close();

 public:
  boost::random::mt19937 gen;
  size_t mOpenCount;
  bool mOpenRet;
  uint8_t mLastMac[MAC_ADDRESS_SIZE];
  size_t mInitCount;
  size_t mLastChannels;
  bool mInitRet;
  size_t mChannelsCount;
  size_t mStartCount;
  bool mStartRet;
  size_t mAcquireCount;
  size_t mAcquireRet;
  size_t mGetDataCount;
  uint32_t* mpLastGetData;
  size_t mLastSamples;
  size_t mTimestampCount;
  uint64_t mTimestampRet;
  size_t mStopCount;
  bool mStopRet;
  size_t mCloseCount;
  bool mCloseRet;	
};

#endif
