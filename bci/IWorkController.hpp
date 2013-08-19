#ifndef IWORK_CONTROLLER_HPP
#define IWORK_CONTROLLER_HPP

#include "Portability.hpp"

class DllExport IWorkController
{
 public:
  virtual ~IWorkController() {}
  virtual bool doWork()=0;
};

#endif
