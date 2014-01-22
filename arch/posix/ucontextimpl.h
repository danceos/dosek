#ifndef UCONTEXTIMPL_H
#define UCONTEXTIMPL_H


#include <ucontext.h>
#include "os/scheduler/task.h"
#include "output.h"
#include <signal.h>
#include "signalinfo.h"
namespace arch {

class PosixContext {
	typedef void (* const fptr_t)(void);

    ucontext_t m_ctxt;
	bool is_fresh;

public:

    PosixContext(void) : is_fresh(false) {};

    void forceinline init(void* stack, size_t stacksize,  fptr_t funcp) {
        debug << "Initializing context: " << &m_ctxt << endl;

        int ret = getcontext(&m_ctxt);
        assert(ret == 0);
        m_ctxt.uc_stack.ss_sp    = stack;
        m_ctxt.uc_stack.ss_size  = stacksize;
        m_ctxt.uc_stack.ss_flags = 0;
        printSigset("init", &m_ctxt.uc_sigmask);
        // clear signal mask
        sigemptyset(&m_ctxt.uc_sigmask);

        // set entry function
        (void)makecontext(&m_ctxt, funcp, 0);
		is_fresh = true;
    }

    void forceinline start(void) {
        //debug << "Starting context: " << &m_ctxt << endl;
		is_fresh = false;
        (void)setcontext(&m_ctxt);
    }

    void forceinline save(void) {
        //debug << "Saving context: " << &m_ctxt << endl;
		is_fresh = false;
        int ret = getcontext(&m_ctxt);
        assert (ret == 0);
    }

    void forceinline saveAndResume(PosixContext& next) {
        // getcontext/setcontext variant:
        // volatile int magic = 1;
        // getcontext(&m_ctxt);
        // magic--;
        // if(magic == 0) {
        //     setcontext(next.getContext());
        // }
		next.is_fresh = false;
		volatile int a = 0;
		debug << "SWAP " << ((void*)&a) << endl;
		a++;
		// volatile int magic = 1;
		// getcontext(&m_ctxt);
		// magic--;
        // if(magic == 0) {
		// 	setcontext(next.getContext());
		// }
        if( swapcontext(&m_ctxt, next.getContext()) == -1 ) {
			perror("swapcontext");
			exit(-1);
		}
		a--;
		debug << "RETURN " << ((void*)&a)<< endl;
		if (a != 0) {
			printf("fooo");
		}
    }

    forceinline ucontext_t* getContext(void) {
        return &m_ctxt;
    }

	forceinline bool wasTerminated() const {
		return is_fresh;
	}
};
}; // endof namespace
#endif
