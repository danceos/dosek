/**
 * @file
 * @ingroup i386
 * @brief i386 system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "os/util/assert.h"
#include "idt.h"
#include "lapic.h"
#include "paging.h"

#define SYSENTER_CS_MSR 0x174  //!< MSR index for sysenter/sysexit kernel GDT offset
#define SYSENTER_ESP_MSR 0x175 //!< MSR index for sysenter %esp value
#define SYSENTER_EIP_MSR 0x176 //!< MSR index for sysenter %eip value

extern "C" uint8_t _estack_os;

namespace arch {
extern void ** const OS_stackptrs[];
extern volatile uint32_t save_sp;

void syscalls_init(void);

#ifdef CONFIG_ARCH_PRIVILEGE_ISOLATION

/**@{*/
/** \brief Run specified function as syscall
 *
 * Currently, any function can be called this way. Eventually, this will be replaced
 * by an (encoded) index to a static jumptable of syscalls
 *
 * \param fun syscall function to be called
 * \param arg1 (optional) argument for syscall
 * \param arg2 (optional) argument for syscall
 * \param arg3 (optional) argument for syscall
 * \tparam direct execute syscall directly in IRQ handler instead of userspace (default: false)
 */
template<bool direct=false, typename F>
forceinline void syscall(F fun) {
	// use clobber instead of pusha to save and restore only required registers:
	// gcc documentation says to list modified input in outputs and they must not be included
	// in clobber list, but LLVM works only the other way ...

	// use int for direct syscalls and sysenter for normal syscalls
	if(!direct) {
		asm volatile(
			"push %%ebp;" // save %ebp
#ifdef CONFIG_DEPENDABILITY_ENCODED
			"mov %%esp, %%ecx;" // save stackptr ...
			"popcnt %%ecx, %%edi;" // ... with odd parity ...
			"xor $0xffffffff, %%edi;"
			"shl $0x1f, %%edi;"
			"or %%ecx, %%edi;" // ... in %edi
			"mov $1f, %%ecx;" // save return address ...
			"popcnt %%ecx, %%ecx;" // ... with odd parity ...
			"xor $0xffffffff, %%ecx;"
			"shl $0x1f, %%ecx;"
			"or $1f, %%ecx;"
			"push %%ecx;" // .. on stack
#else
			"mov %%esp, %%edi;" // save stackptr in %edi
			"push $1f;" // save return address on stack
#endif
			"sysenter;" // start syscall
			"1: pop %%ebp" // return address: restore %ebp
			:: "d"(fun)
			: "ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory"
		);
	} else {
		asm volatile("push %%ebp; int %0; pop %%ebp" :: "i"(IRQ_SYSCALL), "d"(fun) :
			"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
	}
}

template<bool direct=false, typename F, typename A>
	forceinline void syscall(F fun, A arg1) {
	asm volatile("" :: "a"(*((uint32_t*) &arg1)));
	syscall<direct>(fun);
}

template<bool direct=false, typename F, typename A, typename B>
	forceinline void syscall(F fun, A arg1, B arg2) {
	asm volatile("" :: "b"(*((uint32_t*) &arg2)));
	syscall<direct>(fun, arg1);
}

#else // !CONFIG_ARCH_PRIVILEGE_ISOLATION

template<bool direct=false, typename F, typename A=int, typename B=int>
	forceinline void syscall(F fun, A arg1=0, B arg2=0) {
	Machine::disable_interrupts();
    // block ISR2s by raising APIC task priority
	LAPIC::set_task_prio(128);
	// reenable ISR1s
	Machine::enable_interrupts();

#ifdef CONFIG_ARCH_MPU
	// save page directory
	uint32_t pd;
	asm volatile("mov %%cr3, %0" : "=D"(pd));

	// change to OS page directory
	PageDirectory::enable(pagedir_os);
#endif

#ifdef CONFIG_DEPENDABILITY_ENCODED
	uint32_t ssp = save_sp;
	assert( (ssp & 0xFFFF) == (ssp >> 16) );
	void *sp = OS_stackptrs[ssp & 0xFFFF];
#else
	void *sp = OS_stackptrs[save_sp];
#endif
	save_sp = 0; // to detect IRQ from userspace in idt.S

	asm volatile(
		"push %%ebp;" // save %ebp
#ifdef CONFIG_DEPENDABILITY_ENCODED
		"mov %%esp, %%ecx;" // save stackptr ...
		"popcnt %%ecx, %%edi;" // ... with odd parity ...
		"xor $0xffffffff, %%edi;"
		"shl $0x1f, %%edi;"
		"or %%ecx, %%edi;"
		"mov %%edi, (%2);" // ... as saved stack pointer

		"mov $1f, %%ecx;" // save return address ...
		"popcnt %%ecx, %%ecx;" // ... with odd parity ...
		"xor $0xffffffff, %%ecx;"
		"shl $0x1f, %%ecx;"
		"or $1f, %%ecx;"
		"push %%ecx;" // .. on stack
#else
		"mov %%esp, (%2);" // save stackptr in %edi
		"push $1f;" // save return address on stack
#endif
		"mov %1, %%esp;"
		"jmp %P0;"
		"1: pop %%ebp" // return address: restore %ebp
		:: "i"(fun), "i"(&_estack_os - 2048), "S"(sp), "a"(arg1), "b"(arg2)
		: "ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory"
		);

#ifdef CONFIG_ARCH_MPU
// restore page directory
	asm volatile("mov %0, %%cr3" :: "D"(pd));
#endif

}

#endif


/**@}*/

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	// TODO: determine using some (encoded) system variable instead of hardware register?
	return (LAPIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__
