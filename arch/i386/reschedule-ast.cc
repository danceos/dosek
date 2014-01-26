#include "syscall.h"
#include "dispatch.h"
#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "lapic.h"
#include "util/assert.h"
#include "os/scheduler/scheduler.h"

extern "C" uint8_t _estack_os;

namespace arch {

ISR(IRQ_RESCHEDULE) {
	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// set userspace segment selectors
	// TODO: maybe not neccessary?
	Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

	// push the syscall stack address/segment
	Machine::push(GDT::USER_DATA_SEGMENT | 0x3); // push stack segment, DPL3
	Machine::push((uint32_t) &(_estack_os) - 2048); // push kernel stack pointer

	// push flags, IO privilege level 3
	Machine::push(cpu->eflags | 0x3000);

	// push syscall function pointer/segment
	Machine::push(GDT::USER_CODE_SEGMENT | 0x3); // push code segment, DPL3
	Machine::push((uint32_t) os::scheduler::ScheduleC); // push address of scheduler function

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// return from interrupt and proceed with syscall in ring 3
	// TODO: optimization: put all values for iret in text segment?
	Machine::return_from_interrupt();
}

}; // namespace arch
