#ifndef ENOBIO_DATA_RECEIVER_HPP
#define ENOBIO_DATA_RECEIVER_HPP

#include "IEnobioSignalHandler.hpp"
#include "Enobio3G.h"

class EnobioDataReceiver : public IDataConsumer {
public:
    EnobioDataReceiver(IEnobioSignalHandler* pEnobioSignalHandler);
    virtual ~EnobioDataReceiver();
    void registerConsumer(Enobio3G* pEnobio3G);
    void receiveData(const PData& rData);
    
private:
    IEnobioSignalHandler* mpEnobioSignalHandler;
};

#endif