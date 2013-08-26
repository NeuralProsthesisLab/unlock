#ifndef PYNOBIO_HPP
#define PYNOBIO_HPP

#include <Windows.h>

#include "ISignal.hpp"
#include "Enobio3G.h"
#include "channeldata.h"
#include "StatusData.h"
#include "Portability.hpp"

#define BUFFER_SAMPLES 32
#define CHANNELS 8

class EnobioDataConsumer : public IDataConsumer {
public:
	int *buffer;
	int nSamples;
	unsigned long long timestamp;
	HANDLE hEvent;

	EnobioDataConsumer();
	~EnobioDataConsumer();
        
	void receiveData (const PData &data);
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
};


#endif