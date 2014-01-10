#ifndef __MACHINE_H__
#define __MACHINE_H__

#include "os/util/inline.h"

/**
 *  @ingroup arch
 *  @defgroup i386 i386 Hardware
 *  @brief Architecture specific code for the i386 hardware.
 */

/**
 * @file
 *
 * @ingroup i386
 *
 * @brief Machine dependent special instructions.
 */

/**
 * \brief Machine dependent special instructions.
 * This struct provides static forceinline methods implementings some machine 
 * specific instructions.
 */
struct Machine
{
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
		asm volatile ("hlt");
	}

	/**
	 * \brief Emits an undefined instruction trap.
	 * Used for runtime asserts.
	 */
	static forceinline void debug_trap(void) {
		asm volatile ("ud2");
	}

	/**
	 * \brief Push value on stack
	 */
	static forceinline void push(uint32_t val) {
		// try immediate operand first, use register if not possible
		asm volatile("push %0" :: "ir"(val));
	}

	/**
	 * \brief Set data segment selectors (ds, es, fs, gs)
	 */
	static forceinline void set_data_segment(uint16_t selector) {
		asm volatile("mov %0, %%ds; mov %0, %%es; mov %0, %%fs ;mov %0, %%gs" :: "r"(selector));
	}

	/**
	 * \brief Return from interrupt handler
	 */
	static forceinline void return_from_interrupt(void) {
		asm volatile("iret");
		__builtin_unreachable();
	}

	/**
	 * \brief Shutdown machine using ACPI
	 * The static ACPI values used work for QEMU and Bochs but probably not on real PCs!
	 */
	static forceinline void shutdown(void) {
		// write shutdown command to ACPI port
		asm volatile( "outw %0, %1" :: "a"((unsigned short) 0x2000), "Nd"((unsigned short) 0xB004) );

		// stop in case ACPI shutdown failed
		//asm volatile("hlt"); // causes exception when called from ring 3
		while(true) {
			asm("nop");
		}

		__builtin_unreachable();
	}
};

#endif // __MACHINE_H__
