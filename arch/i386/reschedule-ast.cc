#include "syscall.h"
#include "dispatch.h"
#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "lapic.h"
#include "util/assert.h"
#include "os/scheduler/scheduler.h"

namespace arch {

/** \brief */
IRQ_HANDLER(IRQ_RESCHEDULE) {
	// store pointer to context in %esi before we change %esp
	cpu_context* ctx;
	asm volatile("leal -4(%%esp), %0" : "=r"(ctx));

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// TODO: reuse pushed CPU context?
	// move to interrupt stack?
	//asm volatile("mov $_estack_os-2048, %esp");

	// set userspace segment selectors
	// TODO: maybe not neccessary?
	Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

	// push syscall argument
	Machine::push(0);

	// push return adddress
	// provides nice stack backtraces but will not actually work:
	// a return would jump back to the caller without returning to
	// DPL3 and setting the original page directory...
	Machine::push(ctx->eip); // push return address

	// TODO: HACK: use current (interrupt) stack for syscall
	// get current stack pointer
	uint32_t sp;
	asm volatile("mov %%esp, %0" : "=r"(sp));

	// push the syscall stack address/segment
	Machine::push(GDT::USER_DATA_SEGMENT | 0x3); // push stack segment, DPL3
	Machine::push(sp); // push stack pointer

	// push flags, IO privilege level 3
	Machine::push(ctx->eflags | 0x3000);

	// push syscall function pointer/segment
	Machine::push(GDT::USER_CODE_SEGMENT | 0x3); // push code segment, DPL3
	Machine::push((uint32_t) os::scheduler::ScheduleC); // push eip

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// return from interrupt and proceed with syscall in ring 3
	// TODO: optimization: put all values for iret in text segment?
	Machine::return_from_interrupt();
}

}; // namespace arch
