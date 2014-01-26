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

namespace arch {

/** \brief Run specified function as syscall
 *
 * Currently, any function can be called this way. Eventually, this will be replaced
 * by an (encoded) index to a static jumptable of syscalls
 *
 * \param fun syscall function to be called
 * \param arg (optional) argument for syscall
 * \param direct execute syscall directly in IRQ handler instead of userspace (default: false)
 */
template<typename F, typename A=int>
forceinline void syscall(F fun, A arg=0, bool direct=false) {
	// save all registers and call syscall interrupt
	//asm volatile("pusha; int %0; popa" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg)));

	// use clobber instead of pusha to save and restore only required registers:
	// gcc documentation says to list modified input in outputs and they must not be included
	// in clobber list, but LLVM works only the other way ...
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg)), "d"(direct) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	return (LAPIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__