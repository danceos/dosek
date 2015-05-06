#ifndef __ARCH_X86_TCB
#define __ARCH_X86_TCB

#include "os/util/assert.h"
#include "os/util/redundant.h"

namespace arch {

struct TCB {
	typedef void (* const fptr_t)(void);

	// Are we a basic task
	bool basic_task;
	
	// task function
	fptr_t fun;

	// task stack
	void * const stack;

	// reference to saved stack pointer
#ifdef CONFIG_DEPENDABILITY_ENCODED
	const os::redundant::HighParity<void *> sp;
#else
	const os::redundant::Plain<void *> sp;
#endif

	constexpr inline void ** get_tos(void) const {
		return (void **)(((char *)stack) + stacksize);
	}

	constexpr inline void* &running_marker(void) const {
		return *(get_tos() - 1);
	}

	constexpr inline void* &basic_task_frame_pointer(void) const {
		return *(get_tos() - 2);
	}

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
		if (basic_task) {
			// For basic tasks we use a different running marker method
			running_marker() = (void *) 0xaaaaffff;
			return;
		}

		set_sp(get_tos());
	}

	inline bool is_running(void) const {
#ifdef CONFIG_OS_BASIC_TASKS
		if (basic_task)
			return running_marker() != (void *) 0xaaaaffff;
#endif

		return get_sp() != get_tos();
	}

	// This function is called in kickoff methods, which are generated
	// in coder/arch_x86.py!!
	inline void set_running() const {
		// The running marker is only used for basic tasks
		if (basic_task) {
			running_marker() = (void *) 0xa5a5a5a5;
		}
	}

	constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
		: basic_task(stacksize < 16), fun(f), stack(s), sp(sptr), stacksize(stacksize) {}

};

};
#endif
