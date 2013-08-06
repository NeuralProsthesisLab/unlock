#include "fake_bci.hpp"

FakeBCI::FakeBCI() {
}

FakeBCI::~FakeBCI() {
	
}

bool FakeBCI::open(uint8_t[]) {
	return true;
}

bool FakeBCI::init(size_t) {
	return true;
}

bool FakeBCI::start() {
	return true;
}

size_t FakeBCI::acquire() {
	return 1;
}

void FakeBCI::getdata(uint32_t* data, size_t n) {

}

uint64_t FakeBCI::timestamp() {
	return 0;
}

bool FakeBCI::stop() {
	return true;
}

bool FakeBCI::close() {
	return true;
}

