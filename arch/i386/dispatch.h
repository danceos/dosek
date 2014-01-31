/**
 * @file
 * @ingroup i386
 * @brief i386 task dispatching
 */

#ifndef __DISPATCH_H__
#define __DISPATCH_H__

#include "os/util/inline.h"
#include "os/scheduler/task.h"
#include "idt.h"
#include "lapic.h"
#include "machine.h"
#include "syscall.h"



/** \brief Halt the processor when idle */
#define IDLE_HALT 1

/** \brief callback that is called before the idle loop is entered */
extern "C" void __attribute__((weak_import)) __OS_PreIdleHook(void);

namespace arch {

// TODO: remove pointer usage by determining static location from task ID
/** \brief Stack pointer save location */
extern volatile void** save_sp;

extern volatile void* startup_sp;


// next task to dispatch (used by dispatch interrupt)
// TODO: remove redundancy
extern volatile uint32_t dispatch_pagedir;
extern volatile uint32_t dispatch_stackptr;
extern volatile uint32_t dispatch_ip;



class Dispatcher {
public:
	static forceinline void dispatch_syscall(const uint32_t& pagedir, const uint32_t& stackptr, const uint32_t& ip) {
		// set dispatch values
		dispatch_pagedir = pagedir;
		dispatch_stackptr = stackptr;
		dispatch_ip = ip;

		// request dispatcher AST
		LAPIC::trigger(IRQ_DISPATCH);

		// unblock ISR2s by lowering APIC task priority
		// TODO: do this at end of syscall, not here?
		LAPIC::set_task_prio(0);

		// should never come here when called from userspace
		// TODO: remove this check?
		if(Machine::current_ring() > 0) {
			Machine::unreachable();
		}
	}

	static forceinline void Dispatch(const os::scheduler::Task& task) {
		// TODO: remove pointer usage
		save_sp = (volatile void **) &task.sp;

		// TODO: do this in dispatcher IRQ?/control flow check
		if(!task.is_running()) {
			// not resuming, pass task function
			dispatch_syscall((uint32_t) task.id, (uint32_t)task.sp, (uint32_t)task.fun);
		} else {
			// resuming, pass stackpointer with saved IP
			dispatch_syscall((uint32_t) task.id, (uint32_t)task.sp, (uint32_t)&task.sp);
		}
	}

	#if IDLE_HALT

	/** \brief Syscall to start idle loop (in ring 0) */
	static forceinline void idle(void) {
		syscall(&idle_loop, 0, true);
	}

	/** \brief The idle loop
	 *
     * Must be run in ring 0 to allow halting the machine
	 */
	static noinline void idle_loop(void) {
		// allow all interrupts
		LAPIC::set_task_prio(0);

		/* Call the idle loop callback */
		/* Call the idle loop callback */
		if (__OS_PreIdleHook != NULL)
			__OS_PreIdleHook();

		/* enable interrupts and go to sleep */
		while (true) Machine::goto_sleep();

		Machine::unreachable(); // should never come here
	}

	#else // IDLE_HALT

	/** \brief Run idle loop */
	static forceinline void idle(void) {
		// allow all interrupts
		LAPIC::set_task_prio(0);
		Machine::enable_interrupts();

		/* Call the idle loop callback */
		if (__OS_PreIdleHook != NULL)
			__OS_PreIdleHook();

		// do nothing forever
		while(true) Machine::nop();

		Machine::unreachable(); // should never come here
	}

	#endif // IDLE_HALT
};

} // namespace arch

#endif // __DISPATCH_H__
