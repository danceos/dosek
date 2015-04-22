/**
 * @file
 * @ingroup i386
 * @brief i386 system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "gic.h"

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
template<typename F>
forceinline void syscall(F fun) {
	// use clobber instead of pusha to save and restore only required registers:
	// gcc documentation says to list modified input in outputs and they must not be included
	// in clobber list, but LLVM works only the other way ...

	/* We push r7 (frame pointer in thumb mode) and
	   lr (frame pointer in arm mode) here, because
	   neither gcc nor clang are able to obey the
	   clobber of the frame pointer correctly. */
	asm volatile(
				 "push {r7,lr};"
				 "mov r1, sp;" // save stackptr ...
				 "adr r0, $1f; orr r0, r0, #1;" // Add thumb mode bit
				 "push {r0};" // save return address ...
#ifdef CONFIG_DEPENDABILITY_ENCODED
				 "push {r0};" // .. twice
#endif
				 "mov r0, %0;"
				 "svc #0;" // start syscall
				 "1:"
				 "  cps #31;"
				 "  mov sp, r0;"
				 "  pop {r7,lr};" // return
				 :: "r"(fun)
				 : "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
				   "r8", "r9", "r10", "r11", "r12", "memory", "cc"
				 );
}

template<typename F, typename A>
forceinline void syscall(F fun, A arg1) {
    uint32_t a1 = *(uint32_t*) &arg1;
    asm volatile("mov r2, %0" :: "l" (a1) : "r2");
	syscall(fun);
}

template<typename F, typename A, typename B>
forceinline void syscall(F fun, A arg1, B arg2) {
    uint32_t a2 = *(uint32_t*) &arg2;
    asm volatile("mov r3, %0" :: "l" (a2) : "r3");
	syscall(fun, arg1);
}

// template<bool direct=false, typename F, typename A, typename B, typename C>
// forceinline void syscall(F fun, A arg1, B arg2, C arg3) {
//     asm volatile("mov %%r4, %0" :: "irm"(*((uint32_t*) &arg3)));
// 	syscall<direct>(fun, arg1, arg2);
// }

/**@}*/

/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	// TODO: determine using some (encoded) system variable instead of hardware register?
	return (GIC::get_task_prio() == IRQ_PRIO_SYSCALL);
}

} // namespace arch

#endif // __SYSCALL_H__
