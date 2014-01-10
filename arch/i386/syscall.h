/**
 * @file
 * @ingroup i386
 * @brief i386 system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "idt.h"

template<typename F, typename A>
forceinline void syscall(F fun, A arg) {
	// save all registers and call syscall interrupt
	asm volatile("pusha; int %0; popa" :: "i"(IRQ_SYSCALL), "b"(fun), "c"(*((uint32_t*)&arg)));

	// TODO: gcc clobber instead of pusha?
	//asm volatile("int $48" :: "b"(fun), "c"(*((uint32_t*)&arg)) : "eax","edx");
}

namespace arch {

/** \brief Currenty used CPU ring */
forceinline uint8_t current_ring(void) {
	uint32_t flags;
	asm("pushf; pop %%eax" : "=a"(flags));
	return (flags & 0x3000) >> 12;
}


} // namespace arch

#endif // __SYSCALL_H__