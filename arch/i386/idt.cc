/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "idt.h"
#include "gdt.h"
#include "exception.h"
#include "lapic.h"
#include "output.h"

namespace arch {

/** \brief Default handler for interrupts */
ISR(unhandled) {
	// interrupt number passed in %eax
	uint32_t intno;
	asm volatile("" : "=a"(intno));

	// print and halt when debugging
	#if DEBUG
	uint32_t ip = cpu->eip;
	debug << "unhandled interrupt ";
	debug << dec << intno;
	debug << " @ 0x";
	debug << hex << ip;
	debug << endl;

	asm("hlt");
	#endif

	// send end-of-interrupt (unless exception)
	if(intno > 31) LAPIC::send_eoi();
}



extern "C" IDTDescriptor theidt[256];
constexpr InterruptDescriptorTable IDT::idt __attribute__ ((aligned (8))) = {
	sizeof(theidt)-1,
	&theidt[0]
};

void IDT::init() {
	// load static IDT
	asm volatile("lidt %0" : : "m"(IDT::idt) : "memory");
}

}; // namespace arch
