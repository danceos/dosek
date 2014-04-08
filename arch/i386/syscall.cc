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

#if SYSENTER_SYSCALL
	/* Syscalls that run in userspace, this are indirect syscall, they
	   are intended for longer syscalls */
extern "C" __attribute__((naked)) void sysenter_syscall() {
	// get arguments from registers
	void* fun;
	uint32_t arg1, arg2, arg3;
	asm volatile("" : "=a"(arg1), "=b"(arg2), "=S"(arg3), "=d"(fun));

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	asm volatile("mov %%ebp, %0" :: "m"(*save_sp));
	save_sp = 0; // for detecting bugs, not stricly neccessary

	// exit system
	asm volatile("sysexit" :: "a"(arg1), "b"(arg2), "S"(arg3), "c"(&_estack_os - 2048), "d"(fun));
	Machine::unreachable();
}
#endif


#if SYSENTER_SYSCALL

/** \brief Syscall interrupt handler. This handler is used for direct
	syscalls that do not run in userspace, but in kernelmode */
IRQ_HANDLER(IRQ_SYSCALL) {
	// get arguments from registers
	// also, store pointer to context in %esi before we change %esp
	void* fun;
	uint32_t arg1, arg2, arg3;

	asm volatile("" : "=a"(arg1), "=b"(arg2), "=S"(arg3), "=d"(fun));

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	// save page directory
	uint32_t pd;
	asm volatile("mov %%cr3, %0" : "=D"(pd));

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// call syscall function with arguments
	asm volatile("call *%0" :: "r"(fun), "a"(arg1), "b"(arg2), "S"(arg3));

	// restore page directory
	asm volatile("mov %0, %%cr3" :: "D"(pd));

	// reenable ISR2s by resetting APIC task priority
	Machine::disable_interrupts();
	LAPIC::set_task_prio(0);

	// return from interrupt and proceed with caller in ring 3
	Machine::return_from_interrupt();
}

#else // SYSENTER_SYSCALL

/** \brief Syscall interrupt handler */
IRQ_HANDLER(IRQ_SYSCALL) {
	// get arguments from registers
	// also, store pointer to context in %esi before we change %esp
	void* fun;
	uint32_t arg1, arg2, arg3;

	bool direct;
	cpu_context* ctx;
	asm volatile("mov %%esp, %0" : "=r"(ctx), "=a"(arg1), "=b"(arg2), "=S"(arg3), "=d"(fun), "=D"(direct));

	// TODO: remove/reuse pushed CPU context?

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	// syscall to be executed directly in IRQ handler?
	// TODO: derive this from syscall (function)
	if(!direct) {
		#ifndef SYSEXIT_SYSCALL
		// set userspace segment selectors
		// TODO: maybe not neccessary?
		Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

		// save stack+instruction pointer
		if(ctx->cs & 0x3) { // only if coming from userspace
			*save_sp = (void*) ctx->user_esp; // save SP
			*(*((uint32_t **) save_sp) - 1) = ctx->eip; // save IP
			save_sp = 0;
		}

		// push the syscall stack address/segment
		Machine::push(GDT::USER_DATA_SEGMENT | 0x3); // push stack segment, DPL3
		Machine::push((uint32_t) (&_estack_os - 2048)); // push OS stack pointer

		// push flags, IO privilege level 3, interrupts on
		Machine::push(0x3200);

		// push syscall function pointer/segment
		Machine::push(GDT::USER_CODE_SEGMENT | 0x3); // push code segment, DPL3
		Machine::push((uint32_t)fun); // push eip

		// change to OS page directory
		PageDirectory::enable(pagedir_os);

		// return from interrupt and proceed with syscall in ring 3
		// TODO: optimization: put all values for iret in text segment?
		asm volatile("iret" :: "a"(arg1), "b"(arg2), "S"(arg3));
		Machine::unreachable();

		#else // SYSEXIT_SYSCALL

		// save stack+instruction pointer
		if(ctx->cs & 0x3) { // only if coming from userspace
			*save_sp = (void*) ctx->user_esp; // save SP
			*(*((uint32_t **) save_sp) - 1) = ctx->eip; // save IP
			save_sp = 0;
		}

		// change to OS page directory
		PageDirectory::enable(pagedir_os);

		// exit to syscall
		asm volatile("sysexit" :: "a"(arg1), "b"(arg2), "S"(arg3), "c"(&_estack_os - 2048), "d"(fun));
		Machine::unreachable();

		#endif // SYSEXIT_SYSCALL
	} else {
		// save page directory
		uint32_t pd;
		asm volatile("mov %%cr3, %0" : "=D"(pd));

		// change to OS page directory
		PageDirectory::enable(pagedir_os);

		// call syscall function with arguments
		asm volatile("call *%0" :: "r"(fun), "a"(arg1), "b"(arg2), "S"(arg3));

		// restore page directory
		asm volatile("mov %0, %%cr3" :: "D"(pd));

		// reenable ISR2s by resetting APIC task priority
		Machine::disable_interrupts();
		LAPIC::set_task_prio(0);

		// return from interrupt and proceed with caller in ring 3
		Machine::return_from_interrupt();
	}
}
#endif // SYSENTER_SYSCALL

/** \brief Initialize model-specific registers for sysenter/sysexit */
void syscalls_init() {
	Machine::set_msr(SYSENTER_CS_MSR, GDT::KERNEL_CODE_SEGMENT);

	#ifdef SYSENTER_SYSCALL
	Machine::set_msr(SYSENTER_EIP_MSR, (uint64_t) & sysenter_syscall);
	Machine::set_msr(SYSENTER_ESP_MSR, (uint64_t)(&_estack_os - 16));
	#endif
}

}; // namespace arch
