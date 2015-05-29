/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "idt.h"
#include "gdt.h"
#include "exception.h"
#include "machine.h"
#include "lapic.h"
#include "output.h"
#include "hooks.h"

#define CONTINUE_UNHANDLED_IRQ 0

namespace arch {

/** \brief Default handler for interrupts */
ISR(unhandled) {
	// interrupt number passed in %eax
	uint32_t intno;
	asm volatile("" : "=a"(intno));

	// send end-of-interrupt (unless exception)
	if(intno > 31) LAPIC::send_eoi();

	CALL_HOOK(FaultDetectedHook, TRAPdetected, intno, cpu->eip);

	// print and halt when debugging
	uint32_t ip = cpu->eip;
	kout << "unhandled interrupt ";
	kout << dec << intno;
	kout << " @ 0x";
	kout << hex << ip;
	kout << endl;

	Machine::halt();
}



// NMI error handler
IRQ_HANDLER(2) {
	CALL_HOOK(FaultDetectedHook, TRAPdetected, 0, 0);
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
