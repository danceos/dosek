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
	 * \brief Enable all interrupts
	 */
	static forceinline void enable_interrupts() {
		asm volatile("sti\n\tnop");
	}

	/**
	 * \brief Disable all interrupts
	 */
	static forceinline void disable_interrupts() {
		asm volatile("cli");
	}

	/**
	 * \brief Return interrupt enable flag
	 */
	static forceinline bool interrupts_enabled(void) {
		uint32_t flags;
		asm("pushf; pop %0" : "=r"(flags));
		return (flags & 0x0200);
	}

	/**
	 * \brief Return current CPU ring
	 */
	static forceinline uint8_t current_ring(void) {
		uint16_t cs;
		asm("mov %%cs, %0" : "=r"(cs));
		return (cs & 0x3);
	}

	/**
	 * \brief Return from interrupt handler
	 */
	static forceinline void return_from_interrupt(void) {
		asm volatile("iret");
		__builtin_unreachable();
	}

	/**
	 * \brief Unreachable code
	 * Will trigger interrupt if this is actually executed.
	 */
	static forceinline void unreachable(void) {
		asm volatile("int3");
		__builtin_unreachable(); // allow compiler optimization
	}

	/**
	 * \brief Shutdown machine using ACPI
	 * The static ACPI values work for QEMU and Bochs but probably not on real PCs!
	 */
	static forceinline void shutdown(void) {
		// write shutdown command to ACPI port
		asm volatile( "outw %0, %1" :: "a"((unsigned short) 0x2000), "Nd"((unsigned short) 0xB004));

		// stop in case ACPI shutdown failed
		//asm volatile("hlt"); // causes exception when called from ring 3
		while(true) {
			asm("nop");
		}

		__builtin_unreachable();
	}
};

#define __asm_label(a) #a
#define _asm_label(a) __asm_label(a)
#define asm_label(label) asm volatile (".asm_label." label "_%=:" :: "m" (*(void *)0))

#endif // __MACHINE_H__
