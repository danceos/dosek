/**
 * @file
 * @ingroup i386
 * @brief i386 MMU/Paging setup
 */

#include "paging.h"

namespace arch {

void MMU::init() {
	// enable the OS page directory
	PageDirectory::enable(pagedir_os);

	// enable paging and write protection in CR0
	unsigned int cr0;
	asm volatile("mov %%cr0, %0": "=b"(cr0));
	cr0 |= 0x80010000;
	asm volatile("mov %0, %%cr0":: "b"(cr0));
}

}

// Pagefault interrupt handler printing details for debugging
#if DEBUG
#include "idt.h"
#include "output.h"
#include "os/util/inline.h"

namespace arch {

/** \brief Debug pagefault handler
 *
 * Prints invalid address and instruction on debug output.
 */
ISR(14) {
	uint32_t fault_addr, cr3;
	asm("mov %%cr2, %0" : "=r"(fault_addr));
	asm("mov %%cr3, %0" : "=r"(cr3));

	debug << "PAGE FAULT for 0x" << hex << fault_addr;
	debug << ", IP @ 0x" << cpu->eip;
	debug << ", PD @ 0x" << cr3;
	debug << endl;

	asm("hlt");
}

}
#endif // DEBUG
