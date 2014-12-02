#ifndef __ARCH_X86_TCB
#define __ARCH_X86_TCB

#include "os/util/redundant.h"


namespace arch {

struct TCB {
	typedef void (* const fptr_t)(void);

	// task function
	fptr_t fun;

	// task stack
	void * const stack;

	// reference to saved stack pointer
#ifdef ENCODED
	const os::redundant::HighParity<void *> sp;
#else
	const os::redundant::Plain<void *> sp;
#endif

	const int stacksize;

	inline bool check_sp(void) const {
		return sp.check();
	}

	inline void* get_sp(void) const {
		return sp.get();
	}

	inline void set_sp(void* s) const {
		sp.set(s);
	}

	inline void reset(void) const {
		set_sp((uint8_t*)stack + stacksize -4);
	}

	inline uint32_t is_running(void) const {
		return ((uint32_t)get_sp()) ^ (uint32_t)((uint8_t*)stack + stacksize - 4);
	}

	constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
		: fun(f), stack(s), sp(sptr), stacksize(stacksize) {}

};

};
#endif
