#ifndef PYNOBIO_HPP
#define PYNOBIO_HPP

#include <Windows.h>
//#include <boost/mutex.hpp>
#include <boost/thread.hpp>

#include "ISignal.hpp"
#include "Enobio3G.h"
#include "channeldata.h"
#include "StatusData.h"
#include "Portability.hpp"

#define BUFFER_SAMPLES 32768
#define CHANNELS 8

class EnobioDataConsumer : public IDataConsumer {
public:
	uint32_t *buffer;
	size_t nSamples;
	uint64_t timestamp;
	HANDLE hEvent;
        
public:
	EnobioDataConsumer(boost::mutex* pMutex);
	~EnobioDataConsumer(); 
	void receiveData (const PData &data);
        
private:
    boost::mutex* mpMutex;
};

class EnobioStatusConsumer : public IDataConsumer {
public:
	void receiveData (const PData &data);
};

class DllExport Enobio : public ISignal {
public:
	Enobio();
	virtual ~Enobio();
        
public:
	virtual bool open(uint8_t* mac);
	virtual bool init(size_t channels);
        virtual size_t channels();
	virtual bool start();
	virtual size_t acquire();
	virtual void getdata(uint32_t* buffer, size_t samples);
	virtual uint64_t timestamp();
	bool stop();
	bool close();

private:
   
	Enobio3G enobio;
	EnobioDataConsumer *enobioData;
	EnobioStatusConsumer *enobioStatus;

	bool opened;
	bool started;
	size_t* samples;
	size_t nChannels;
        boost::mutex mutex;
};


#endif