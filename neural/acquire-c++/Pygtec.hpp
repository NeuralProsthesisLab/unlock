#ifndef PYGTEC_H
#define PYGTEC_H

#include <Windows.h>
#include "gmobilabplus.h"

class MOBIlab {
private:
	HANDLE devptr;
	short *buffer;
	_BUFFER_ST datbuffer;
	OVERLAPPED ov;
public:
	MOBIlab();
	~MOBIlab();
	BOOL open(LPSTR);
	BOOL init(const int, const int);
	BOOL start();
	BOOL acquire();
	void getdata(int *data, int n);
	BOOL stop();
	BOOL close();
};

#endif