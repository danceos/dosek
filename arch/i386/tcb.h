#ifndef __ARCH_X86_TCB
#define __ARCH_X86_TCB

#include "os/util/assert.h"
#include "arch/i386/i386.h"

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
		#if PARITY_CHECKS
		return (__builtin_parity((uint32_t) sp) == 1);
		#else
		return true;
		#endif
	}

	inline void* get_sp(void) const {
		#if PARITY_CHECKS
		return (void *) ((uint32_t)sp & 0x7FFFFFFF);
		#else
		return sp;
		#endif
	}

	inline void set_sp(void* s) const {
		#if PARITY_CHECKS
		uint32_t _sp = (uint32_t) s;
		if(__builtin_parity(_sp) == 1) {
			sp = s;
		} else {
			sp = (void*) (_sp | 0x80000000);
		}
		#else
		sp = s;
		#endif
	}

	inline void reset(void) const {
		set_sp((uint8_t*)stack + stacksize - 16);
	}

	inline bool is_running(void) const {
		return get_sp() != (uint8_t*)stack + stacksize - 16;
	}

	constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
		: fun(f), stack(s), sp(sptr), stacksize(stacksize) {}

};

};
#endif
