/**
 * @file
 * @ingroup i386
 * @brief i386 system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "irq.h"

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

	// use int for direct syscalls and sysenter for normal syscalls
	if(!direct) {
        //uint32_t sp;
        //asm volatile("mov %0, sp" : "=r"(sp));
        //kout << "SVC before: " << hex << sp << endl;

        asm volatile(
            "push {lr};"
		 	"mov r1, sp;" // save stackptr ...
		 	"mov r0, $1f; push {r0};" // save return address ...
            "mov r0, %0;"
		 	"svc #0;" // start syscall
		 	"1: pop {lr}" // return address: restore %ebp
            :: "Ir"(fun)
            : "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "memory", "cc"
        );


        //asm volatile("mov %0, sp" : "=r"(sp));
        //kout << "SVC after: " << hex << sp << endl;
	} else {
		// asm volatile("push %%ebp; int %0; pop %%ebp" :: "i"(IRQ_SYSCALL), "d"(fun) :
		// 	"ebx", "ecx", "eax", "edx", "ebp", "esi", "edi", "cc", "memory");
	}
}

template<bool direct=false, typename F, typename A>
forceinline void syscall(F fun, A arg1) {
	asm volatile("mov %%r2, %0" :: "irm"(*((uint32_t*) &arg1)));
	syscall<direct>(fun);
}

template<bool direct=false, typename F, typename A, typename B>
forceinline void syscall(F fun, A arg1, B arg2) {
    asm volatile("mov %%r3, %0" :: "irm"(*((uint32_t*) &arg2)));
	syscall<direct>(fun, arg1);
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
	return (GIC::get_task_prio() == 128);
}

} // namespace arch

#endif // __SYSCALL_H__
