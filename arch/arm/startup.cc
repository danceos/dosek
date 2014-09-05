/**
 * @file
 * @ingroup ARM
 * @brief Architecture-specific startup code
 */

#include <stdint.h>
#include "irq.h"
#include "mmu.h"
#include "timer.h"
#include "syscall.h"
#include "output.h"
#include "machine.h"

/** Initialisation stub for generic startup code */
extern "C" void init_generic();
extern "C" void run_constructors(void);

using namespace arch;


extern "C" __attribute__((naked)) void test_syscall() {
    kout << "HELLO WORLD" << endl;

    // trigger interrupt
    GIC::trigger(0);

    kout << "aHA!" << endl;

    GIC::set_task_prio(255);

    asm volatile("b .");
}

//!< i386 specific startup code
extern "C" void arch_startup()
{
    kout << "Booted" << endl;

    //wait_for_debugger();

    // setup generic interrupt controller
    GIC::init();
    GIC::set_irq_priority(0, 254);

        // switch to user mode preversing SP
    uint32_t sp;
    asm volatile("mov %0, sp" : "=r"(sp));
    Machine::switch_mode(Machine::USER);
    asm volatile("mov sp, %0" :: "r"(sp));

//            Machine::enable_interrupts();


#if 0
/****** TESTING *******/
    //Machine::syscall(1);

    kout << "Foo" << endl;
    GIC::trigger(2);
    kout << "Bar" << endl;
    GIC::trigger(3);
    kout << "w00t" << endl;

    Machine::enable_interrupts();
    kout << "xy" << endl;
    GIC::trigger(4);
    kout << "zzy" << endl;


    kout << "X" << endl;



    kout << "A" << endl;

    //Machine::debug_trap(1);

    syscall(test_syscall);

    kout << "B" << endl;

    Machine::shutdown();
/****** TESTING *******/
#endif

    /*
    // setup system stack
    // TODO

	// setup paging
	#ifndef MPU_DISABLED
	MMU::init();
	#endif

	// setup PIT
	PIT::init();
    */

    // run constructors of global objects
    run_constructors();

	// Proceed to generic initialisation
	init_generic();
}
