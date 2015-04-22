/**
 * @file
 * @ingroup i386
 * @brief Architecture-specific startup code
 */

#include "gdt.h"
#include "idt.h"
#include "paging.h"
#include "pic.h"
#include "lapic.h"
#include "ioapic.h"
#include "pit.h"
#include "syscall.h"

/** Initialisation stub for generic startup code */
extern "C" void init_generic();
extern "C" void run_constructors(void);

using namespace arch;

//!< i386 specific startup code
extern "C" void arch_startup()
{
	// setup GDT, IDT
	GDT::init();
	IDT::init();

    // setup sysenter/sysexit
    syscalls_init();

	// setup paging
	#ifdef CONFIG_ARCH_MPU
    	MMU::init();
	#endif

	// setup PIC
	PIC::init();

	// setup local APIC
	LAPIC::init();

	// setup I/O APIC
	IOAPIC::init();

	// setup PIT
	PIT::init();


    // run constructors of global objects
    run_constructors();

	// TODO: enable interrupts somewhere?
	// here, before os_main, or in a future StartOS()

	// Proceed to generic initialisation
	init_generic();
}
