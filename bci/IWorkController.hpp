#ifndef IWORK_CONTROLLER_HPP
#define IWORK_CONTROLLER_HPP

class IWorkController {
public:
    virtual ~IWorkController() {}
    virtual bool doWork()=0;
};

#endif
