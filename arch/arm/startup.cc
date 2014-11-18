/**
 * @file
 * @ingroup ARM
 * @brief Architecture-specific startup code
 */

#include <stdint.h>
#include "gic.h"
#include "mmu.h"
#include "timer.h"
#include "syscall.h"
#include "output.h"
#include "machine.h"

/** Initialisation stub for generic startup code */
extern "C" void init_generic();
extern "C" void run_constructors(void);

extern "C" {
	__attribute__((section(".kernel_stack"))) char os_stack[4096];
}

using namespace arch;

//!< arm specific startup code
extern "C" void arch_startup()
{
    // run constructors of global objects
    run_constructors();

	Machine::setup_caches();

    kout << "Booted" << endl;

    //wait_for_debugger();

    // setup generic interrupt controller
    GIC::init();
    GIC::set_irq_priority(IRQ_DISPATCH, IRQ_PRIO_DISPATCH);
    GIC::set_irq_priority(IRQ_RESCHEDULE, IRQ_PRIO_RESCHEDULE);

    /*
    // setup system stack
    // TODO

	// setup paging
	#ifndef MPU_DISABLED
	MMU::init();
	#endif

    */

    // setup Private Timer
	Timer::init();

    //Machine::enable_interrupts(); // DEBUG TODO
    //while(1); // DEBUG TODO

    // switch to user mode preserving SP
    uint32_t sp;
    asm volatile("mov %0, sp" : "=r"(sp));
    Machine::switch_mode(Machine::USER);
    asm volatile("mov sp, %0" :: "r"(sp));

	// unblock ISR2s by lowering GIC task priority
	GIC::set_task_prio(IRQ_PRIO_LOWEST);

    kout << "SSSSSS [[[[[[ Starting dOSEK ]]]]]]" << endl;
	kout << "APP_BOOT" << endl;
	// Proceed to generic initialisation
	init_generic();
}
