
// Copyright (c) James Percent and Unlock contributors.
// All rights reserved.
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//    1. Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//    
//    2. Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//    3. Neither the name of Unlock nor the names of its contributors may be used
//       to endorse or promote products derived from this software without
//       specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
// ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
// ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "Logger.hpp"
#include <iostream>
#include <ctime>

const std::string Logger::currentDateTime() {
    time_t     now = time(0);
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime(&now);
    strftime(buf, sizeof(buf), "%Y-%m-%d.%X", &tstruct);
    return buf;
}

double Logger::currentTimeMilliSecs() {
    return 1000*Logger::currentTimeMicroSecs();
}

double Logger::currentTimeMicroSecs() {
    return time(0);
}

Logger::Logger(const std::string& name) : mName(name), mMode(Logger::CONSOLE | Logger::FILE), mOpened(false) {
    std::cerr << "M Mode = " << (int)mMode << "---" <<  std::endl;
    tryOpen();
}

Logger::~Logger() {
    if(mOpened) {
        mLog.close();
        mOpened = false;
    }
}

void Logger::setMode(uint8_t mode) {
    uint8_t oldMode = mMode;
    mMode = mode;
    if((mMode & Logger::FILE) != 0 && !mOpened) {
       tryOpen();
    }
}

void Logger::debug(const std::string& msg) {
    logit("DEBUG", msg, std::cout, mMode);
}

void Logger::info(const std::string& msg) {
    logit("INFO", msg, std::cout, mMode);    
}

void Logger::warn(const std::string& msg) {
    logit("WARN", msg, std::cout, mMode);
}

void Logger::error(const std::string& msg) {
    logit("ERROR", msg, std::cerr, mMode | Logger::CONSOLE);
}

void Logger::fatal(const std::string& msg) {
    logit("FATAL", msg, std::cerr, mMode | Logger::CONSOLE);    
}

void Logger::logit(const std::string& prefix, const std::string& msg, std::ostream& out, uint8_t mode) {
    volatile bool locked = false;
    
    std::cerr << msg << " MODE == " << (int)mode << std::endl;
    
    if ((mMode & Logger::SYNC) != 0) {
        locked = true;
        mMutex.lock();
    }
    
    std::string date_time = Logger::currentDateTime();
    if((mMode & Logger::CONSOLE) != 0) {
        out << date_time << ": " << prefix << " " << msg << std::endl;
    } 
    
    if((mMode & Logger::FILE) != 0) {
        mLog << date_time << ": " << prefix << " " << msg << std::endl;
    }
    
    if(locked) {
        mMutex.unlock();
    }
}

void Logger::tryOpen() {
    try {
        mLog.open(mName);
        mOpened = true;
    } catch(...) {
        mMode = mMode ^ Logger::FILE;
        error("failed to open logger file");
    }    
}

