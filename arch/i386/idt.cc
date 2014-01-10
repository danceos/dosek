/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "idt.h"
#include "gdt.h"
#include "exception.h"

#if DEBUG
#include "serial.h"
extern Serial serial;
#endif

namespace arch {

/** \brief Default handler for interrupts */
extern "C" __attribute__((naked)) void unhandled_handler() {
	// get context pointer and int# from registers
	struct task_context* ctx;
	uint32_t intno;
	asm("" : "=S"(ctx), "=a"(intno));

	// print and halt when debugging
	#if DEBUG
	serial << "unhandled interrupt ";
	serial << intno;
	serial << " @ 0x";
	serial << hex << ctx->cpu_context.eip;
	serial << endl;

	asm("hlt");
	#endif

	// jump to exit code
	asm volatile("jmp handler_exit" :: "S"(ctx));
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
