/**
 * @file
 * @ingroup i386
 * @brief i386 Local Advanced Programmable Interrupt Controller (local APIC)
 */

#include "lapic.h"
#include "pic.h"

namespace arch {

void LAPIC::init() {
	// enable APIC
	enable();

	// disable PIC
	PIC::disable();
}

}; // namespace arch
