/**
 * @file
 * @ingroup posix
 * @brief Posix system call interface
 */

#ifndef __SYSCALL_H__
#define __SYSCALL_H__

#include "os/util/inline.h"
#include "machine.h"
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
forceinline void syscall(const F fun, A arg=0, __attribute__((unused)) bool direct=false) {
    Machine::disable_interrupts();
    fun(arg);
    Machine::enable_interrupts();
}


/** \brief Return true if calling code is running as part of a syscall */
forceinline bool in_syscall() {
	return !irq.in_interrupt(); // When we are in an interrupt, we are
								// not coming from an systemcall
}

} // namespace arch

#endif // __SYSCALL_H__
