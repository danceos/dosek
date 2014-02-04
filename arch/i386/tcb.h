#ifndef __ARCH_X86_TCB
#define __ARCH_X86_TCB

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



	inline void reset(void) const {
		sp = (uint8_t*)stack + stacksize - 16;
	}

	inline bool is_running(void) const {
		return sp != (uint8_t*)stack + stacksize - 16;
	}

    constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
	 	: fun(f), stack(s), sp(sptr), stacksize(stacksize) {}

};

};
#endif
