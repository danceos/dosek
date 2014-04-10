#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "tcb.h"
#include "os/util/inline.h"
#include "os/util/assert.h"
#include "os/util/encoded.h"
#include "lapic.h"
#include "i386.h"

/** \brief Enable task dispatching using sysexit instead of iret */
#define SYSEXIT_DISPATCH 1

extern "C" arch::TCB * const OS_tcbs[];

namespace arch {

/** \brief Startup stackpointer (save location) */
volatile void* startup_sp = 0;
volatile uint32_t save_sp = 0;

#ifdef ENCODED
volatile Encoded_Static<A0, 42> dispatch_task;
#else
volatile uint16_t dispatch_task;
#endif

/** \brief Dispatch interrupt handler
 *
 * This interrupt is called after the next task is determined by the scheduler in ring 3
 * and performs the actual dispatching in ring 0.
 */
IRQ_HANDLER(IRQ_DISPATCH) {
	#ifdef ENCODED
	// decode task ID
	uint16_t id = dispatch_task.decode();
	#else
	uint16_t id = dispatch_task;
	#endif

	// get TCB
	const TCB * const tcb = OS_tcbs[id];

	// set save_sp
	save_sp = id | ((id) << 16);

#ifndef SYSEXIT_DISPATCH
	// push stack segment, DPL3
	Machine::push(GDT::USER_DATA_SEGMENT | 0x3);

	// push stack pointer
	#if PARITY_CHECKS
	uint32_t *sp = (uint32_t *) tcb->get_sp();
	assert(tcb->check_sp());
	#else
	uint32_t *sp = (uint32_t *) tcb->sp;
	#endif

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
	if(tcb->is_running()) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ip = (uint32_t) *(sp - 1);

		#if PARITY_CHECKS
		assert(__builtin_parity(ip) == 1);
		Machine::push(ip & 0x7FFFFFFF);
		#else
		Machine::push(ip);
		#endif

		*(sp - 1) = 0; // clear IP to prevent this from remaining valid in memory
	} else {
		// start function from beginning
		Machine::push(tcb->fun);
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
	#if PARITY_CHECKS
	uint32_t *sp = (uint32_t *) tcb->get_sp();
	assert(tcb->check_sp());
	#else
	uint32_t *sp = (uint32_t *) tcb->sp;
	#endif
	if(tcb->is_running()) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ipv = (uint32_t) *(sp - 1);

		#if PARITY_CHECKS
		assert(__builtin_parity(ipv) == 1);
		ip = (void*) (ipv & 0x7FFFFFFF);
		#else
		ip = (void*) ipv;
		#endif

		*(sp - 1) = 0; // clear IP to prevent this from remaining valid in memory
	} else {
		// start function from beginning
		ip = (void*) tcb->fun;
	}

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// exit system at IO privilege level 3 with IRQs disabled
	Machine::sysexit(ip, sp, 0x3000);

#endif // SYSEXIT_DISPATCH
}

} // namespace arch
