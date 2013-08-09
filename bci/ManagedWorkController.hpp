#ifndef MANAGED_WORK_CONTROLLER_HPP
#define MANAGED_WORK_CONTROLLER_HPP

#include <boost/atomic.hpp>
#include "IWorkController.hpp"

class ManagedWorkController : public IWorkController
{
public:
    ManagedWorkController(bool startState);
    virtual ~ManagedWorkController();
    virtual bool doWork();
    void setDoWorkState(bool state);
    
private:
    boost::atomic<bool> mState;
};

#endif
