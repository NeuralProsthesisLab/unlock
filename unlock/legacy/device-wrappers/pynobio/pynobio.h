#ifndef PYNOBIO_H
#define PYNOBIO_H

#include <Windows.h>
#include <stdio.h>
#include "Enobio3G.h"
#include "channeldata.h"
#include "StatusData.h"

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

class Enobio {
private:
	Enobio3G enobio;
	EnobioDataConsumer *enobioData;
	EnobioStatusConsumer *enobioStatus;

	BOOL opened;
	BOOL started;
	int *samples;
	int nChannels;
public:
	Enobio();
	~Enobio();
	BOOL open();
	BOOL init(const int);
	BOOL start();
	BOOL acquire();
	void getdata(int *data, int n);
	unsigned long long timestamp();
	BOOL stop();
	BOOL close();
};


#endif