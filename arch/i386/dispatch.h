/**
 * @file
 * @ingroup i386
 * @brief i386 task dispatching
 */

#ifndef __DISPATCH_H__
#define __DISPATCH_H__

#include "os/util/inline.h"
#include "os/util/encoded.h"
#include "os/scheduler/task.h"
#include "os/hooks.h"
#include "idt.h"
#include "lapic.h"
#include "machine.h"
#include "syscall.h"
#include "tcb.h"



/** \brief Halt the processor when idle */
#define IDLE_HALT 1

namespace arch {

extern volatile void* startup_sp;

extern volatile uint32_t save_sp;

// next task to dispatch (used by dispatch interrupt)
#ifdef CONFIG_DEPENDABILITY_ENCODED
extern volatile Encoded_Static<A0, 42> dispatch_task;
#else
extern volatile uint16_t dispatch_task;
#endif

class Dispatcher {

#ifdef CONFIG_ARCH_IDLE_HALT
	/** \brief The idle loop
	 *
	 * Must be run in ring 0 to allow halting the machine
	 */
	static noinline void idle_loop() {
		/* Call the idle loop callback (does end with
		   Machine::enable_interrupts())*/
		CALL_HOOK(PreIdleHook);

		// allow all interrupts
		LAPIC::set_task_prio(0);

		/* enable interrupts and go to sleep */
		while (true) Machine::goto_sleep();

		Machine::unreachable(); // should never come here
	}
#endif

	static forceinline void dispatch_syscall(const os::scheduler::Task& task) {
	// set task to dispatch
#ifdef CONFIG_DEPENDABILITY_ENCODED
		dispatch_task.encode(task.id);
#else
		dispatch_task = task.id;
#endif

        // Call PreTaskHook.
        CALL_HOOK(PreTaskHook);

		// request dispatcher AST
		LAPIC::trigger(IRQ_DISPATCH);

		// unblock ISR2s by lowering APIC task priority
		LAPIC::set_task_prio(0);

		// This is a wait period for qemu to trigger the interrupt in
		// time.
		while(1) Machine::nop();
	}

public:

	static forceinline void Prepare(const os::scheduler::Task& task) {
        task.tcb.reset();
		// For basic tasks we have to prepare the SP checksum, since
		// the compiler does not use set_sp, but plain addresses.
		if (task.tcb.basic_task) {
			task.tcb.set_sp(task.tcb.get_sp());
		}
	}

	static forceinline void Destroy(const os::scheduler::Task& task) {
		task.tcb.reset();
		/* If the terminated task is a basic task, we have to reset
		 * the shared stack pointer */
		if (/* always static */ task.tcb.basic_task) {
			task.tcb.set_sp(task.tcb.basic_task_frame_pointer());
		}
	}

	static forceinline void Dispatch(const os::scheduler::Task& task,
									 const os::scheduler::Task *last = 0) {
		(void) last;
		dispatch_syscall(task);
	}

	static forceinline void ResumeToTask(const os::scheduler::Task& task,
										 const os::scheduler::Task *last = 0) {
		(void) last;
		dispatch_syscall(task);
	}

	static forceinline void StartToTask(const os::scheduler::Task& task,
										const os::scheduler::Task *last = 0) {
		(void) last;
		dispatch_syscall(task);
	}


	/** \brief Syscall to start idle loop (in ring 0) */
	static forceinline void Idle(void) {
#ifdef CONFIG_ARCH_IDLE_HALT
		syscall<true>(&idle_loop);
#else // IDLE_HALT

		/* Call the idle loop callback (does end with
		   Machine::enable_interrupts())*/
		CALL_HOOK(PreIdleHook);

		// allow all interrupts
		LAPIC::set_task_prio(0);

		// do nothing forever
		while(true) Machine::nop();

		Machine::unreachable(); // should never come here
#endif // CONFIG_IDLE_HALT
	}

};

} // namespace arch

#endif // __DISPATCH_H__
