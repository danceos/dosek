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

/** Initialisation stub for generic startup code */
extern void init_generic();
extern "C" void run_constructors(void);

using namespace arch;

//!< i386 specific startup code
extern "C" void arch_startup()
{
	// setup GDT, IDT
	GDT::init();
	IDT::init();

	// setup paging
	MMU::init();

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
