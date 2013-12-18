/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "idt.h"
#include "gdt.h"
#include "exception.h"

#if DEBUG
#include "paging.h"
#include "serial.h"
extern Serial serial;
#endif

namespace arch {

/** \brief Saved stackframe for interrupt/trap/syscall */
struct stackframe {
	// saved registers
	// TODO: dont save eax, ecx, edx (caller save) when syscalling?
	uint32_t edi, esi, ebp, esp, ebx;
	uint32_t edx, ecx, eax;

	// pushed by specific IRQ handler
	uint32_t int_no;
	uint32_t error_code;

	// pushed by CPU
	uint32_t eip;
	uint32_t cs;
	uint32_t eflags;

	// pushed by CPU when coming from userspace
	uint32_t user_esp;
	uint32_t ss;
};



#if DEBUG
/** \brief Debug pagefault handler
 *
 * Prints invalid address on serial console.
 */
void pf_handler(struct stackframe &sf) {
	uint32_t fault_addr;

	asm("mov %%cr2, %0" : "=r"(fault_addr));
	serial << "PAGE FAULT for 0x" << hex << fault_addr << ", IP @ 0x" << sf.eip << endl;
}
#endif



/** \brief Assembly code to return from interrupt */
extern "C" void handler_exit();

/** \brief IRQ handler
 *
 * This function is not called, but jumped to by the individual IRQ handlers,
 * and a pointer to the saved stack frame is passed in register ESI. To exit
 * IRQ handling a jump to `handler_exit` is neccessary.
 * This is done as inlining this function call from the assembly handlers is not
 * possible and a call from assembly pushes a fragile unencoded return address.
 */
extern "C" __attribute__((naked)) void irq_handler() {
	// the saved stack frame (passed in %esi)
	struct stackframe* sf;
	asm("nop" : "=S"(sf));

	switch(sf->int_no) {
		#if DEBUG
		case PAGE_FAULT:
			pf_handler(*sf);
			break;
		#endif
		default:
			#if DEBUG
			serial << "unhandled interrupt ";
			serial << sf->int_no;
			serial << " @ 0x";
			serial << hex << sf->eip;
			serial << endl;
			#endif
			break;
	};

	// jump to exit code
	asm volatile("jmp handler_exit" :: "S"(sf));
}



// IRQ handler table constants
constexpr uint32_t HANDLER_BASE = 0x101000; //!< IRQ handlers start address
constexpr uint32_t HANDLER_SIZE = 0x10; //!< IRQ handler size in bytes

// the static IDT
constexpr IDTDescriptor IDT::descriptors[] __attribute__ ((aligned (8))) = {
	{HANDLER_BASE + 0*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 1*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 2*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{}, //{HANDLER_BASE + 3*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 4*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 5*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 6*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 7*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{}, //{HANDLER_BASE + 8*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 9*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 10*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 11*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 12*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{}, //{HANDLER_BASE + 13*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 14*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{}, // RESERVED
	{HANDLER_BASE + 15*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 16*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 17*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 18*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{HANDLER_BASE + 19*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
	{}, {}, {}, {}, {}, {}, {}, {}, {}, // RESERVED
	{HANDLER_BASE + 20*HANDLER_SIZE, GDT::KERNEL_CODE_SEGMENT, TYPE_DPL0_IRQ_GATE},
};

// the static IDT register
constexpr InterruptDescriptorTable IDT::idt __attribute__ ((aligned (8))) = {
	sizeof(IDT::descriptors)-1,
	&IDT::descriptors[0]
};



void IDT::init() {
	// load static IDT
	asm volatile("lidt %0" : : "m"(IDT::idt) : "memory");
}

}; // namespace arch
