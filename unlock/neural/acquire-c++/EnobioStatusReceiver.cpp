
#include <boost/assert.hpp>

#include "StatusData.h"
#include "EnobioStatusReceiver.hpp"

EnobioStatusReceiver::EnobioStatusReceiver(IEnobioSignalHandler* pEnobioSignalHandler)
    : mpEnobioSignalHandler(pEnobioSignalHandler){    
}

EnobioStatusReceiver::~EnobioStatusReceiver() {
}

void EnobioStatusReceiver::registerConsumer(Enobio3G* pEnobio3G) {
    BOOST_VERIFY(pEnobio3G != 0);
	pEnobio3G->registerConsumer(Enobio3G::STATUS, *this);
}

void EnobioStatusReceiver::receiveData(const PData& rData) {
    BOOST_VERIFY(mpEnobioSignalHandler != 0);
    mpEnobioSignalHandler->handleStatusData((StatusData *)rData.getData());
}
