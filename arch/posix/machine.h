#ifndef __MACHINE_H__
#define __MACHINE_H__


#include "os/util/inline.h"

/**
 *  @ingroup arch
 *  @defgroup posix Posix "Hardware" abstraction
 *  @brief Architecture specific code for the posix "hardware".
 */

/**
 * @file
 *
 * @ingroup posix
 *
 * @brief Machine dependent special instructions.
 */

/**
 * \brief Machine dependent special instructions.
 * This struct provides static forceinline methods implementing some machine
 * specific instructions.
 */
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>
#include "signalinfo.h"
#include "output.h"
#include "irq.h"


class Machine
{
public:

    static void init(void) {
        debug << "Machine::init()" << endl;
		arch::irq.disable_interrupts();
    }

	/**
	 * \brief Emits a nop opcode. (nop)
	 */
	static forceinline void nop(void) {
		asm volatile ("nop");
	};

	/**
	 * \brief Halts the machine. (hlt)
	 */
	static forceinline void halt(void) {
        //pause();
        sigset_t mask;
        sigemptyset(&mask);
        sigsuspend(&mask);
	}

	/**
	 * \brief Emits an undefined instruction trap.
	 * Used for runtime asserts.
	 */
	static forceinline void debug_trap(void) {
        debug.setcolor(Color::BLUE, Color::WHITE);
        debug << "Machine::debug_trap !" << endl;
		exit(EXIT_FAILURE);
	}


	/**
	 * \brief Disable all interrupts
	 */
	static forceinline void disable_interrupts() {
		arch::irq.disable_interrupts();
    }

	/**
	 * \brief Enable all interrupts
	 */
	static forceinline void enable_interrupts() {
		arch::irq.enable_interrupts();
    }

	/**
	 * \brief Unreachable code
	 * Will trigger interrupt if this is actually executed.
	 */
	static noinline void unreachable(void) {
        debug.setcolor(Color::WHITE, Color::RED);
		arch::irq.disable_interrupts();
        kout << ("ERROR: We reached unreachable code!\n");
		abort();
		while(1) {};
        exit(EXIT_FAILURE);
		__builtin_unreachable(); // allow compiler optimization
	}


	/**
	 * \brief Shutdown machine using ACPI
	 * The static ACPI values used work for QEMU and Bochs but probably not on real PCs!
	 */
	static forceinline void shutdown(void) {
        debug.setcolor(Color::BLACK, Color::WHITE);
        debug << ("Machine::shutdown!\n");
		// No unreachable() here, otherwise the generator will be unhappy!
		syscall(SYS_exit, 0);

	}

	/**
	 * \brief Trigger an interrupt
	 */
	static forceinline void trigger_interrupt(uint8_t irq_) {
		arch::irq.trigger_interrupt(irq_);
	}
	static forceinline void trigger_interrupt_from_user(uint8_t irq_) {
		arch::irq.trigger_interrupt(irq_);
	}

};

#endif // __MACHINE_H__
