#ifndef __MACHINE_H__
#define __MACHINE_H__

#include "os/util/inline.h"
#include "lapic.h"
#include "output.h"

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
	 * \brief halt processor atomically
	 */
	static forceinline void goto_sleep() {
		asm volatile("sti\n\thlt");
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
	 * \brief Trigger a software interrupt
	 *
	 * Trigger a synchronous software interrupt using the int(errupt)
	 * instruction.
	 *
	 * On i386 this will call the interrupt routine even when interrupts
	 * are disabled.
	 */
	static forceinline void software_interrupt(uint8_t irq) {
		asm volatile("int %0" :: "i"(irq));
	}

	/**
	 * \brief Trigger a non-software interrupt
	 *
	 * Trigger an asynchronous interrupt which looks to the system
	 * like a hardware interrupt. This is probably only
	 * useful for tests and debugging.
	 *
	 * On i386 this interrupt is triggered using the local APIC.
	 */
	static forceinline void trigger_interrupt(uint8_t irq) {
		arch::LAPIC::trigger(irq);
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
		unreachable();
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
		#if DEBUG
		// don't really shutdown when debugging
		debug << "ACPI shutdown requested" << endl;
		#else
		// write shutdown command to ACPI port
		asm volatile( "outw %0, %1" :: "a"((unsigned short) 0x2000), "Nd"((unsigned short) 0xB004));
		#endif

		// stop in case ACPI shutdown failed
		//halt(); // causes exception when called from ring 3
		while(true) nop();

		unreachable();
	}
};

#define __asm_label(a) #a
#define _asm_label(a) __asm_label(a)
#define asm_label(label) asm volatile (".asm_label." label "_%=:" :: "m" (*(void *)0))

#endif // __MACHINE_H__
