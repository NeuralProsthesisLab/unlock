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

