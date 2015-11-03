#ifndef __OSEKV_TCB_H
#define __OSEKV_TCB_H

#include "output.h"

extern "C" {
	void __switch_to(void * from, void *to);
	void __start_to(void *to);
}

namespace arch {
	struct TCB {
#ifndef CONFIG_OS_SYSTEMCALLS_WIRED
		/* CPU-specific state of a task */
		struct dynamic_state {
			/* Callee-saved registers */
			unsigned long ra;
			unsigned long sp;	/* Kernel mode stack */
			unsigned long s[12];	/* s[0]: frame pointer */
			bool running_marker;
		};

	private:
		typedef void (* const fptr_t)(void);

		// task function
		fptr_t fun;

		// task stack
		void * const stack;

		// reference to saved stack pointer
		const int stacksize;

	public:

		dynamic_state &state;


		inline bool is_running(void) const {
			return state.running_marker;
		}

		inline void set_running() const {
			state.running_marker = true;
		}

		inline void reset(void) const {
			state.running_marker = false;
			// kout << "Fun: " << (void*)fun << endl;
			state.ra = reinterpret_cast<unsigned long>(fun);
			state.sp = reinterpret_cast<unsigned long>(stack) + stacksize;
		}

		void start(const TCB *old) const {
			(void) old;
			set_running();
			// kout << "Start to RA " << hex << this->state.ra << endl;
			// Lets go to an extended stack
			__start_to(&this->state);
		}

		void switchTo(const TCB *other) const {
			other->set_running();
			// kout << "Switch to RA " << hex << this->state.ra << " to " << other->state.ra << endl;
			__switch_to(&this->state, &other->state);
		}

		constexpr TCB(fptr_t f, void *stack_ptr, dynamic_state &state, int stacksize)
	    : fun(f), stack(stack_ptr), stacksize(stacksize), state(state)  {}
		
#else
		TCB(){}
#endif
	};
}

#endif
