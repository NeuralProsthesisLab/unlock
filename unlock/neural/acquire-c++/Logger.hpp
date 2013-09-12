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
public:
    Logger(const std::string& name);
    virtual ~Logger();
    void setMode(uint8_t mode);
    
public:
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