/**
 * @file
 * @ingroup i386
 * @brief i386 system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "idt.h"
#include "lapic.h"

/** \brief Perform syscalls using sysenter insteaf of int */
#define SYSENTER_SYSCALL 1

/** \brief Perform syscall dispatching using sysexit instead of iret */
#define SYSEXIT_SYSCALL 1

#define SYSENTER_CS_MSR 0x174  //!< MSR index for sysenter/sysexit kernel GDT offset
#define SYSENTER_ESP_MSR 0x175 //!< MSR index for sysenter %esp value
#define SYSENTER_EIP_MSR 0x176 //!< MSR index for sysenter %eip value

namespace arch {

void syscalls_init(void);

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

#if SYSENTER_SYSCALL
	// use int for direct syscalls and sysenter for normal syscalls
	if(!direct) {
		asm volatile(
			"push %%ebp;"
			"mov %%esp, %%edi;"
			"push $1f;"
			"sysenter;"
			"1: pop %%ebp"
			:: "d"(fun)
			: "ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory"
		);
	} else {
		asm volatile("push %%ebp; int %0; pop %%ebp" :: "i"(IRQ_SYSCALL), "d"(fun) :
			"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
	}
#else // SYSENTER_SYSCALL
	asm volatile("push %%ebp; int %0; pop %%ebp" :: "i"(IRQ_SYSCALL), "d"(fun), "D"(direct) :
				 "ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
#endif // SYSENTER_SYSCALL
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

template<bool direct=false, typename F, typename A, typename B, typename C>
forceinline void syscall(F fun, A arg1, B arg2, C arg3) {
	asm volatile("" :: "S"(*((uint32_t*) &arg3)));
	syscall<direct>(fun, arg1, arg2);
}

/**@}*/

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	// TODO: determine using some (encoded) system variable instead of hardware register?
	return (LAPIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__
