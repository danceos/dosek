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

/** \brief Run specified function with argument as syscall
 *
 * Currently, any function can be called this way. Eventually, this will be replaced
 * by an (encoded) index to a static jumptable of syscalls.
 */
template<typename F, typename A>
forceinline void syscall(F fun, A arg) {
	// save all registers and call syscall interrupt
	//asm volatile("pusha; int %0; popa" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg)));

	// use clobber instead of pusha:
	// gcc documentation says to list modified input in outputs and they must not be included
	// in clobber list, but LLVM works only the other way ...
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg)) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	return (LAPIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__