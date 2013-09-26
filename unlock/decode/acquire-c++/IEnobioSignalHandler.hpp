#ifndef IENOBIO_SIGNAL_HANDLER_HPP
#define IENOBIO_SIGNAL_HANDLER_HPP

#include "ChannelData.h"
#include "StatusData.h"

class IEnobioSignalHandler
{
 public:
  virtual ~IEnobioSignalHandler() {}
  virtual void handleStatusData(StatusData* pStatusData)=0;
  virtual void handleChannelData(ChannelData* pChannelData)=0;
};

#endif
