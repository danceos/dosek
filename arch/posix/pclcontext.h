#ifndef PCLCONTEXT_H
#define PCLCONTEXT_H


#include <pcl.h>
#include "os/scheduler/task.h"

#include "output.h"

namespace arch {

class PosixContext {
    coroutine_t m_ctxt;
    int id;
    typedef void(*pclfun)(void*);
public:

    PosixContext(void) : m_ctxt(0),  id(-2) {};

    void forceinline init(const os::scheduler::Task& task){
        init(task.stack, task.stacksize, task.fun, task.id);
    }

    void forceinline init(void* stack, size_t stacksize, os::scheduler::Task::fptr_t funcp, int tid = -2) {

          if(m_ctxt != 0) {
            debug << "Deleting context " << m_ctxt << endl;
            co_delete(m_ctxt);
          }

          if(stacksize < 4096) {
            stacksize = 4096;
            stack = NULL;
          }

          debug << "initializing context: " << m_ctxt << endl;
          m_ctxt = co_create((pclfun)funcp,0, stack, stacksize);
          id = tid;
    }


    void forceinline saveAndResume(PosixContext& next) {
          co_call(next.getContext());
    }


    int getId(void) const {
        return id;
    }

    forceinline coroutine_t& getContext(void) {
        return m_ctxt;
    }
};


}; //end of namespace
#endif
