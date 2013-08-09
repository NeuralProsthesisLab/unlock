#include "IntegralWorkController.hpp"

IntegralWorkController::IntegralWorkController(size_t iterations) :mThreshold(iterations), mCount(0) {
}

IntegralWorkController::~IntegralWorkController() {
}

bool IntegralWorkController::doWork() {
    mCount++;
    if (mCount > mThreshold) {
        return false;
    } else {
        return true;
    }
}

