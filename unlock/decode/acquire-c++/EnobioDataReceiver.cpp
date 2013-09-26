
#include <boost/assert.hpp>

#include "ChannelData.h"
#include "EnobioDataReceiver.hpp"

EnobioDataReceiver::EnobioDataReceiver(IEnobioSignalHandler* pEnobioSignalHandler) : mpEnobioSignalHandler(pEnobioSignalHandler){
}

EnobioDataReceiver::~EnobioDataReceiver() {
}

void EnobioDataReceiver::registerConsumer(Enobio3G* pEnobio3G) {
    BOOST_VERIFY(pEnobio3G != 0);
    pEnobio3G->registerConsumer(Enobio3G::ENOBIO_DATA, *this);
}
    	
void EnobioDataReceiver::receiveData(const PData& rData) {
    BOOST_VERIFY(mpEnobioSignalHandler != 0);
    mpEnobioSignalHandler->handleChannelData((ChannelData *)rData.getData());
}
