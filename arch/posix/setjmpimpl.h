#ifndef SETJMPIMPL_H
#define SETJMPIMPL_H


#include <setjmp.h>
#include "os/scheduler/task.h"
#include "output.h"

namespace arch {

class PosixContext {
    sigjmp_buf m_ctxt;
    int id;
public:

    PosixContext(void) : id(-2) {};

    void forceinline init(const os::scheduler::Task& task){
        init(task.stack, task.stacksize, task.fun, task.id);
    }

    void forceinline init(void* stack, size_t stacksize, os::scheduler::Task::fptr_t funcp, int tid = -2) {
        debug << "Initializing context: " << &m_ctxt << endl;
        debug << "  Stack size: " << stacksize  << "Wordsize: " << __WORDSIZE<< endl;

        id = tid;
        if(sigsetjmp(m_ctxt, 1) != 0) {
            Machine::unreachable();
        }

        m_ctxt[0].__jmpbuf[0].__sp = (long)stack;
        m_ctxt[0].__jmpbuf[0].__pc = (long)funcp;

    }

    void forceinline start(void) {
        //debug << "Starting context: " << &m_ctxt << endl;
        //(void)setcontext(&m_ctxt);
    }

    void forceinline save(void) {
        //debug << "Saving context: " << &m_ctxt << endl;
        //getcontext(&m_ctxt);
    }

    void forceinline saveAndResume(PosixContext& next) {
        //swapcontext(&m_ctxt, next.getContext());
        if(sigsetjmp(m_ctxt, 1) == 0) {
            siglongjmp(next.getContext(), 1);
        }
    }


    int getId(void) const {
        return id;
    }


    forceinline sigjmp_buf& getContext(void) {
        return m_ctxt;
    }
};
}; // endof namespace
#endif
