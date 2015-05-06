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

extern void** OS_stackptrs[];

/* Syscalls that run in userspace, this are indirect syscall, they
   are intended for longer syscalls */
extern "C" __attribute__((naked)) void sysenter_syscall() {
	// get arguments from registers
	void *fun, *sp;
	uint32_t arg1, arg2, arg3;
	asm volatile("" : "=a"(arg1), "=b"(arg2), "=S"(arg3), "=d"(fun), "=D"(sp));

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	// save stack pointer

#ifdef CONFIG_DEPENDABILITY_ENCODED
	uint32_t ssp = save_sp;
	assert( (ssp & 0xFFFF) == (ssp >> 16) );
	*OS_stackptrs[ssp & 0xFFFF] = sp;
#else
	*OS_stackptrs[save_sp] = sp;
#endif
	save_sp = 0; // to detect IRQ from userspace in idt.S

	// This is needed to do kout in the initial system call
	// asm volatile("push %0; popf; " :: "ia"(0x3200));

	// exit system
	asm volatile("sysexit" :: "a"(arg1), "b"(arg2), "S"(arg3), "c"(&_estack_os - 2048), "d"(fun));
	Machine::unreachable();
}



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



/** \brief Initialize model-specific registers for sysenter/sysexit */
void syscalls_init() {
	Machine::set_msr(SYSENTER_CS_MSR, GDT::KERNEL_CODE_SEGMENT);

	Machine::set_msr(SYSENTER_EIP_MSR, (uint64_t) & sysenter_syscall);
	Machine::set_msr(SYSENTER_ESP_MSR, (uint64_t)(&_estack_os - 16));
}

}; // namespace arch
