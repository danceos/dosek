/**
 * @file
 * @ingroup i386
 * @brief i386 Local Advanced Programmable Interrupt Controller (local APIC)
 */

#include "lapic.h"
#include "pic.h"
#include "idt.h"
#include "machine.h"
#include "output.h"

/** \brief Counter for spurious interrupts
 *
 * Maybe useful for detecting hardware errors on real hardware
 * and software errors in emulation.
 * Not put in arch namespace to be writable from all page directories.
 */
volatile uint32_t spurious_interrupts = 0;

namespace arch {

void LAPIC::init() {
	// enable APIC
	enable();

	// disable PIC
	PIC::disable();
}


/** \brief Spurious interrupt handler */
IRQ_HANDLER(255) {
	// count spurious interrupt
	spurious_interrupts++;

	// output warning if debugging
	debug << "spurious interrupt!" << endl;

	// return without EOI for spurious interrupt
	Machine::return_from_interrupt();
}

}; // namespace arch
