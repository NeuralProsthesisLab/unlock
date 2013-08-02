#ifndef PYPOC_H
#define PYPOC_H

#include <Windows.h>
#include "EmoStateDLL.h"
#include "edk.h"
#include "edkErrorCode.h"

class EPOC {
private:
	EmoEngineEventHandle eEvent;
	EmoStateHandle eState;
	DataHandle hData;
	int nChannels;
	EE_DataChannel_t *channels;
	unsigned int userId;
	double *samples;
	BOOL ready;
	BOOL closed;
public:
	EPOC();
	~EPOC();
	BOOL open();
	BOOL init(const int);
	BOOL start();
	BOOL acquire();
	void getdata(int *data, int n);
	BOOL stop();
	BOOL close();
};


#endif