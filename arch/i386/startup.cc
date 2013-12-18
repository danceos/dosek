/**
 * @file
 * @ingroup i386
 * @brief Architecture-specific startup code
 */

#include "gdt.h"
#include "idt.h"
#include "paging.h"

/** Initialisation stub for generic startup code */
extern void init_generic();

using namespace arch;

//!< i386 specific startup code
extern "C" void arch_startup()
{
	// setup GDT, IDT
	GDT::init();
	IDT::init();

	// setup paging
	MMU::init();

	// Proceed to generic initialisation
	init_generic();
}
