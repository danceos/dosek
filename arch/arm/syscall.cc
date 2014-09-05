#include "syscall.h"
#include "dispatch.h"
#include "irq.h"
#include "machine.h"
#include "util/assert.h"

extern "C" uint8_t _estack_os;

namespace arch {

extern void** OS_stackptrs[];

/* Syscalls that run in userspace, this are indirect syscall, they
   are intended for longer syscalls */
extern "C" __attribute__((naked)) void syscall_handler(void *fun, void *sp, uint32_t arg1, uint32_t arg2) {
    // change to OS page directory
    //PageDirectory::enable(pagedir_os);

    // block ISR2s by raising APIC task priority
    GIC::set_task_prio(128);

    // reenable ISR1s
    Machine::enable_interrupts();

    // save stack pointer
    uint32_t ssp = save_sp;
    assert( (ssp & 0xFFFF) == (ssp >> 16) );
    *OS_stackptrs[ssp & 0xFFFF] = sp;
    save_sp = 0; // to detect IRQ from userspace in idt.S

    // exit system
    Machine::set_spsr(0x30);

    // set user SP
    Machine::switch_mode(Machine::SYSTEM);
    asm volatile("mov sp, %0" :: "r"(&_estack_os - 2048));
    Machine::switch_mode(Machine::SUPERVISOR);

    asm volatile("mov lr, %0" :: "r"(fun));
    asm volatile("subs pc, lr, #0");
    Machine::unreachable();

#if 0
    kout << "SYSCALL END" << endl;

    // exit system
    //asm volatile("sysexit" :: "a"(arg1), "b"(arg2), "S"(arg3), "c"(&_estack_os - 2048), "d"(fun));
   // asm volatile("pop {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12}"); ///:::
        //"r0","r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12");
    //asm volatile("add sp, sp, #4");
    //asm volatile("add sp, sp, #52");
    //asm volatile("pop {lr}");
    //uint32_t tmp,tmp2;
    //asm volatile("ldr %0, [sp]" : "=r"(tmp));
    //asm volatile("ldr %0, [sp,#4]" : "=r"(tmp2));
    //kout << "RETURN PC:" << hex << tmp << endl;
    //kout << "RETURN PSR:" << hex << tmp << endl;
    //asm volatile("b .");
    //asm volatile("pop {lr}");
    //asm volatile("subs pc, lr, #0");
    asm volatile("mov lr, %0" :: "r"(return_address));
    asm volatile("subs pc, lr, #0");
    //asm volatile("b handler_exit"); // LDM sp!, {pc}^
    Machine::unreachable();
#endif
}

#if 0
/** \brief Syscall interrupt handler. This handler is used for direct
	syscalls that do not run in userspace, but in kernelmode */
IRQ_HANDLER(IRQ_SYSCALL) {
	// get arguments from registers
	// also, store pointer to context in %esi before we change %esp
	void* fun;
	uint32_t arg1, arg2, arg3;

	// asm volatile("" : "=a"(arg1), "=b"(arg2), "=S"(arg3), "=d"(fun));

	// block ISR2s by raising APIC task priority
	// LAPIC::set_task_prio(128);

	// reenable ISR1s
	Machine::enable_interrupts();

	// save page directory
	uint32_t pd;
	// asm volatile("mov %%cr3, %0" : "=D"(pd));

	// change to OS page directory
	PageDirectory::enable(pagedir_os);

	// call syscall function with arguments
	// asm volatile("call *%0" :: "r"(fun), "a"(arg1), "b"(arg2), "S"(arg3));

	// restore page directory
	// asm volatile("mov %0, %%cr3" :: "D"(pd));

	// reenable ISR2s by resetting APIC task priority
	Machine::disable_interrupts();
	// LAPIC::set_task_prio(0);

	// return from interrupt and proceed with caller in ring 3
	Machine::return_from_interrupt();
}
#endif

}; // namespace arch
