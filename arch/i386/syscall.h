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
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "d"(direct) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

template<bool direct=false, typename F, typename A>
forceinline void syscall(F fun, A arg1) {
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg1)), "d"(direct) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

template<bool direct=false, typename F, typename A, typename B>
forceinline void syscall(F fun, A arg1, B arg2) {
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg1)), "d"(direct),
		"a"(*((uint32_t*)&arg2)) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

template<bool direct=false, typename F, typename A, typename B, typename C>
forceinline void syscall(F fun, A arg1, B arg2, C arg3) {
	asm volatile("int %0" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg1)), "d"(direct),
		"a"(*((uint32_t*)&arg2)), "D"(*((uint32_t*)&arg3)) :
		"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
}

/**@}*/

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	// TODO: determine using some (encoded) system variable instead of hardware register?
	return (LAPIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__
