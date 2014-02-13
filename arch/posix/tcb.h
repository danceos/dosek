#ifndef __ARCH_POSIX_TCB
#define __ARCH_POSIX_TCB

#include  "machine.h"
#include "os/util/assert.h"

extern "C" void kickoff();

namespace arch {

struct TCB {
	typedef void (* const fptr_t)(void);

	// task function
	fptr_t fun;

	// task stack
	void * const stack;

	// reference to saved stack pointer
	// TODO: encode?
	void* &sp;

	const int stacksize;
	
	inline void ** get_tos(void) const {
		void **tos = (void **)(((char *)stack) + stacksize);
		return tos;
	}


	inline void reset(void) const {
		void **tos = get_tos();
		*(--tos) = (void *) 0xaaaaffff; // is fresh
		*(--tos) = (void *)kickoff;
		*(--tos) = 0; // %rbx (%ebx)
		*(--tos) = 0; // %r12 (%esi)
		*(--tos) = 0; // %r13 (%edi)
		*(--tos) = 0; // %r14 (%ebp)

		sp = tos;
		assert (!is_running ());
	}

	void start(void) const {
		void *dummy;
		_switchTo(&dummy, &sp);
	}

    void switchTo(const TCB *other) const {
		_switchTo(&sp, &(other->sp));
	}

    static noinline void _switchTo(void **from, void **to) {
        asm __volatile__ ("push %%ebx\n"
                          "push %%esi\n"
                          "push %%edi\n"
                          "push %%ebp\n"
                          "mov  %%esp, %0\n"
                          "mov  %1, %%esp\n"
                          "pop  %%ebp\n"
                          "pop  %%edi\n"
                          "pop  %%esi\n"
                          "pop  %%ebx\n"
                          : "=m" (*from)
                          : "m" (*to)
                          : "memory"
                          );
    }

	inline bool is_running(void) const {
		void **tos = get_tos();
		return *(tos - 1) != (void *) 0xaaaaffff;
	}

	inline void set_running(void) const {
		void **tos = get_tos();
		*(tos - 1) = (void *) 0xa5a5a5a5;
	}


    constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
	 	: fun(f), stack(s), sp(sptr),  stacksize(stacksize) {}

};

};
#endif
