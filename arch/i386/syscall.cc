#include "syscall.h"
#include "dispatch.h"
#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "lapic.h"
#include "util/assert.h"

extern "C" uint8_t _estack_os;

namespace arch {

/** \brief Syscall interrupt handler */
IRQ_HANDLER(IRQ_SYSCALL) {
	// get arguments from registers
	// also, store pointer to context in %esi before we change %esp
	uint32_t fun, arg1, arg2, arg3;
	bool direct;
	cpu_context* ctx;
	asm volatile("mov %%esp, %0" : "=r"(ctx), "=c"(arg1), "=a"(arg2), "=D"(arg3), "=b"(fun), "=d"(direct));

	// TODO: remove/reuse pushed CPU context?

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	// syscall to be executed directly in IRQ handler?
	// TODO: derive this from syscall (function)
	if(!direct) {
		// set userspace segment selectors
		// TODO: maybe not neccessary?
		Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

		// save stack+instruction pointer
		if(ctx->cs & 0x3) { // only if coming from userspace
			*save_sp = (void*) ctx->user_esp; // save SP
			*(*((uint32_t **) save_sp) - 1) = ctx->eip; // save IP
			save_sp = 0; // for detecting bugs, not stricly neccessary
		}

		// put syscall arguments on top kernel stack
		uint32_t* sp = (uint32_t*) (&_estack_os - 2048);
		*sp = arg3;
		*(sp-1) = arg2;
		*(sp-2) = arg1;

		// push the syscall stack address/segment
		Machine::push(GDT::USER_DATA_SEGMENT | 0x3); // push stack segment, DPL3
		Machine::push((uint32_t)(sp-3)); // push stack pointer above argument

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
	} else {
		// save page directory
		uint32_t pd;
		asm volatile("mov %%cr3, %0" : "=S"(pd));

		// change to OS page directory
		PageDirectory::enable(pagedir_os);

		// call syscall function with argument
		// C code does not work as compiler overwrites our return address with arg
		//void (* f)(uint32_t) = (void (*)(uint32_t))fun; f(arg);
		asm volatile("push %3; push %2; push %1; call *%0; pop %1; pop %2; pop %3" :: "r"(fun), "r"(arg1), "r"(arg2), "r"(arg3));

		// restore page directory
		asm volatile("mov %0, %%cr3" :: "S"(pd));

		// reenable ISR2s by resetting APIC task priority
		Machine::disable_interrupts();
		LAPIC::set_task_prio(0);

		// return from interrupt and proceed with caller in ring 3
		Machine::return_from_interrupt();
	}
}

}; // namespace arch
