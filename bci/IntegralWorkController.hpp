#ifndef INTEGRAL_WORK_CONTROLLER_HPP
#define INTEGRAL_WORK_CONTROLLER_HPP

#include <cstddef>

#include "IWorkController.hpp"

class IntegralWorkController : public IWorkController {
public:
    IntegralWorkController(size_t iterations);
    virtual ~IntegralWorkController();
    virtual bool doWork();

private:
    size_t mThreshold;
    size_t mCount;
};

#endif
