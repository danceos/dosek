#include "syscall.h"
#include "dispatch.h"
#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"

namespace arch {

/** \brief Syscall interrupt handler */
IRQ_HANDLER(IRQ_SYSCALL) {
	// get arguments from registers
	// also, store pointer to context in %esi before we change %esp
	uint32_t arg, fun;
	cpu_context* ctx;
	asm volatile("mov %%esp, %0" : "=r"(ctx), "=c"(arg), "=b"(fun));

	// TODO: remove/reuse pushed CPU context?

	// move to interrupt stack
	asm volatile("mov $_estack_os-2048, %esp");

	// set userspace segment selectors
	// TODO: maybe not neccessary?
	Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

	// save stack+instruction pointer
	*save_sp = (void*) ctx->user_esp; // save SP
	*(*((uint32_t **) save_sp) - 1) = ctx->eip; // save IP

	// push argument+return adddress for actual syscall function
	Machine::push(arg); // push argument
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
	Machine::push(fun); // push eip

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// return from interrupt and proceed with syscall in ring 3
	// TODO: optimization: put all values for iret in text segment?
	Machine::return_from_interrupt();
}

}; // namespace arch
