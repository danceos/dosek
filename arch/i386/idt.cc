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

#define CONTINUE_UNHANDLED_IRQ 0

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

	#if CONTINUE_UNHANDLED_IRQ
	// send end-of-interrupt (unless exception)
	if(intno > 31) LAPIC::send_eoi();
	#else // CONTINUE_UNHANDLED_IRQ
	// panic on unhandled interrupts
	Machine::panic();
	#endif // CONTINUE_UNHANDLED_IRQ
}



// NMI error handler
IRQ_HANDLER(2) {
	// TODO: anything useful left to do?
	debug << "PANIC" << endl;

	Machine::halt();
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
