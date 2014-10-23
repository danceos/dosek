#ifndef __ARCH_X86_TCB
#define __ARCH_X86_TCB

#include "os/util/assert.h"

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

	inline bool check_sp(void) const {
		return (__builtin_parity((uint32_t) sp) == 1);
	}

	inline void* get_sp(void) const {
		return (void *) ((uint32_t)sp & 0x7FFFFFFF);
	}

	inline void set_sp(void* s) const {
		uint32_t _sp = (uint32_t) s;
		if(__builtin_parity(_sp) == 1) {
			sp = s;
		} else {
			sp = (void*) (_sp | 0x80000000);
		}
	}

	inline void reset(void) const {
		set_sp((uint8_t*)stack + stacksize -4);
	}

	inline bool is_running(void) const {
		return get_sp() != (uint8_t*)stack + stacksize - 4;
	}

	constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
		: fun(f), stack(s), sp(sptr), stacksize(stacksize) {}

};

};
#endif
