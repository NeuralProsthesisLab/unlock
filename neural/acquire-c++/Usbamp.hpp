#ifndef USBAMP_H
#define USBAMP_H

#include <Windows.h>
#include <deque>
#include "gUSBamp.h"

class USBamp {
private:
	deque<LPSTR> callSequence;
	deque<HANDLE> devices;
public:
	USBamp();
	~USBamp();
	bool open(LPSTR);
	bool init(const int, const int);
	bool start();
	bool acquire();
	void getdata(int *data, int n);
	bool stop();
	bool close();
};

#endif