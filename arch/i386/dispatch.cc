#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "os/util/inline.h"
#include "lapic.h"

/** \brief Enable task dispatching using sysexit instead of iret */
#define SYSEXIT_DISPATCH 1

namespace arch {

/** \brief Startup stackpointer (save location) */
volatile void* startup_sp = 0;
volatile uint32_t save_sp = 0;

volatile uint32_t dispatch_pagedir;
volatile uint32_t dispatch_stackptr;
volatile uint32_t dispatch_ip;

/** \brief Dispatch interrupt handler
 *
 * This interrupt is called after the next task is determined by the scheduler in ring 3
 * and performs the actual dispatching in ring 0.
 */
IRQ_HANDLER(IRQ_DISPATCH) {
	// get dispatch values
	uint32_t id = dispatch_pagedir;
	uint32_t fun = dispatch_ip;
	void* sp = (void*) dispatch_stackptr;

	save_sp = id | ((id) << 16);

#ifndef SYSEXIT_DISPATCH
	// push stack segment, DPL3
	Machine::push(GDT::USER_DATA_SEGMENT | 0x3);

	// push stack pointer
	Machine::push(sp);

	// push flags, IO privilege level 3
	// TODO: always enable interrupts? (0x3200)
	uint32_t flags; // flags are at %esp+16 because of pushed values
	asm volatile("mov 16(%%esp), %0" : "=r"(flags));
	flags |= 0x3000;
	flags &= ~(0x200); // Disable interrupts when dispatching
	Machine::push(flags);

	// push code segment, DPL3
	Machine::push(GDT::USER_CODE_SEGMENT | 0x3);

	// set new page directory
	MMU::switch_task(id);

	// set userspace segment selectors
	// TODO: maybe not neccessary?
	Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

	// push instruction pointer
	if(fun >= 0x200000) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ip = *(*((uint32_t**) fun) - 1);
		Machine::push(ip);
	} else {
		// start function from beginning
		Machine::push(fun);
	}

	// TODO: check prepared stack? (SSE crc32q?)

	// clear all registers
	Machine::clear_registers();

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// return from interrupt
	Machine::return_from_interrupt();

#else // SYSEXIT_DISPATCH

	// set new page directory
	MMU::switch_task(id);

	// push instruction pointer
	void* ip;
	if(fun >= 0x200000) {
		// resume from saved IP on stack
		// requires new page directory set before!
		ip = (void*) *(*((uint32_t**) fun) - 1);
	} else {
		// start function from beginning
		ip = (void*) fun;
	}

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// exit system at IO privilege level 3 with IRQs disabled
	Machine::sysexit(ip, sp, 0x3000);

#endif // SYSEXIT_DISPATCH
}

} // namespace arch
