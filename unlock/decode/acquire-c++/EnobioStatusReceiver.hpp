#ifndef ENOBIO_STATUS_RECEIVER_HPP
#define ENOBIO_STATUS_RECEIVER_HPP

#include "Enobio3G.h"
#include "IEnobioSignalHandler.hpp"

class EnobioStatusReceiver : public IDataConsumer {
public:
	EnobioStatusReceiver(IEnobioSignalHandler* pEnobioSignalHandler);
	virtual ~EnobioStatusReceiver();
    void registerConsumer(Enobio3G* pEnobio3G);
	void receiveData(const PData& rData);
    
private:
    IEnobioSignalHandler* mpEnobioSignalHandler;        
};

#endif