
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

#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <boost/thread.hpp>
#include <fstream>
#include <string>
#include <stdint.h>

#include "Portability.hpp"

class DllExport Logger {
public:
    static const int CONSOLE=0x1;
    static const int FILE=0x2;
    static const int SYNC=0x4;
    
    static const std::string currentDateTime();
    static double currentTimeMilliSecs();
    static double currentTimeMicroSecs();
    
public:
    Logger(const std::string& name);
    virtual ~Logger();
    void setMode(uint8_t mode);
    
    void debug(const std::string& msg);
    void info(const std::string& msg);
    void warn(const std::string& msg);
    void error(const std::string& msg);
    void fatal(const std::string& msg);

private:
    void logit(const std::string& prefix, const std::string& msg, std::ostream& out, uint8_t mode);
    void tryOpen();
    
private:
    boost::mutex mMutex;
    std::ofstream mLog;
    std::string mName;
    uint8_t mMode;
    bool mOpened;
};

#define logError(msg) error(msg)
#define logFatal(msg) fatal(msg)
    
#ifdef NPL_DEBUG
    #define logDebug(msg) debug(msg)
    #define logInfo(msg) info(msg)
    #define logWarn(msg) debug(msg)
#elif NPL_INFO
    #define logDebug(msg) 
    #define logInfo(msg) info(msg)
    #define logWarn(msg) warn(msg)
#elif NPL_WARN
    #define logDebug(msg) 
    #define logInfo(msg) 
    #define logWarn(msg) warn(msg)
#endif

#endif