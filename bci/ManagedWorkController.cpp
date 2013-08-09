#include "ManagedWorkController.hpp"

ManagedWorkController::ManagedWorkController(bool startState)
    : mState(startState)
{
}

ManagedWorkController::~ManagedWorkController()
{
}

bool ManagedWorkController::doWork() {
    return mState.load(boost::memory_order_consume);
}

void ManagedWorkController::setDoWorkState(bool state) {
   mState.store(state, boost::memory_order_consume);   
}

