#ifndef __MACHINE_H__
#define __MACHINE_H__

#include "os/util/inline.h"
#include "lapic.h"
#include "exception.h"
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
		__builtin_unreachable();
	}

	/**
	 * \brief Panic when error is detected
	 *
	 * Triggers non-maskable error interrupt
	 */
	static forceinline void panic(void) {
		// TODO: APIC NMI request instead of software interrupt?
		asm volatile ("int %0" :: "i"(arch::Exceptions::NMI));
	}

	/**
	 * \brief Push value on stack
	 */
	static forceinline void push(uint32_t val) {
		// try immediate operand first, use register if not possible
		asm volatile("push %0" :: "ir"(val) : "esp");
	}

	/**
	 * \brief Reset all general-purpose registers to 0
	 */
	static forceinline void clear_registers() {
		asm volatile("xor %%eax, %%eax" ::: "eax");
		asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		asm volatile("xor %%ecx, %%ecx" ::: "ecx");
		asm volatile("xor %%edx, %%edx" ::: "edx");
		asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		asm volatile("xor %%esi, %%esi" ::: "esi");
		asm volatile("xor %%edi, %%edi" ::: "edi");
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
	static void trigger_interrupt_from_user(uint8_t irq);

	/**
	 * \brief Unreachable code
	 * Will trigger interrupt if this is actually executed.
	 */
	static forceinline void unreachable(void) {
		asm volatile("int3");
		__builtin_unreachable(); // allow compiler optimization
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
	 * \brief Exit to ring 3 and continue with given IP and SP
	 */
	static forceinline void sysexit(void* ip, void* sp) {
		// clear unused registers
		asm volatile("xor %%eax, %%eax" ::: "eax");
		asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		asm volatile("xor %%esi, %%esi" ::: "esi");
		asm volatile("xor %%edi, %%edi" ::: "edi");

		asm volatile("sysexit" :: "d"(ip), "c"(sp));
		unreachable();
	}

	/**
	 * \brief Set flags and exit to ring 3 and continue with given IP and SP and IRQs enabled
	 */
	static forceinline void sysexit_with_sti(void* ip, void* sp, uint32_t flags) {
		// clear unused registers
		asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		asm volatile("xor %%esi, %%esi" ::: "esi");
		asm volatile("xor %%edi, %%edi" ::: "edi");

		// set flags without interrupt enable flag, then use sti to enable IRQs *after* sysexit
		asm volatile("push %0; popf; xor %%eax, %%eax; sti; sysexit" :: "ia"(flags & ~0x0200), "d"(ip), "c"(sp));
		unreachable();
	}

	/**
	 * \brief Set flags and exit to ring 3 and continue with given IP and SP
	 */
	static forceinline void sysexit(void* ip, void* sp, uint32_t flags) {
		// clear unused registers
		asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		asm volatile("xor %%esi, %%esi" ::: "esi");
		asm volatile("xor %%edi, %%edi" ::: "edi");

		// set flags without interrupt enable flag, then use sti to enable IRQs *after* sysexit
		asm volatile("push %0; popf; xor %%eax, %%eax; sysexit" ::
					 "ia"(flags), "d"(ip), "c"(sp));
		unreachable();
	}
	/**
	 * 8042 reset
	 */
	static void reboot(void) {
		uint8_t temp;
		Machine::disable_interrupts();
		/* Clear keyboard buffers */
		do {
			temp = inb(0x64); // 0x64: Keyboard Interface: empty user data
			if(temp & 1) {
				inb(0x60); // empty keyboard data
			}
		} while(temp & 2);
		outb(0x64, 0xFE); // Pulse CPU reset line
		while(1) {
			Machine::halt(); // last resort, loop forever, even on NMIs...
		}
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
		// if the above did not work (as in qemu-system-i386 v2.1.0, we fall through to a reset
		Machine::reboot();
		#endif

		// No unreachable() here, otherwise the generator will be unhappy!
		// stop in case ACPI shutdown failed
		//halt(); // causes exception when called from ring 3
		// while(true) nop();
	}

	/**
	 * \brief Read model-specific register
	 */
	static forceinline void get_msr(uint32_t msr, uint32_t &lo, uint32_t &hi) {
		asm volatile("rdmsr" : "=a"(lo), "=d"(hi) : "c"(msr));
	}

	/**
	 * \brief Read model-specific register
	 */
	static forceinline uint64_t get_msr(uint32_t msr) {
		uint32_t lo, hi;
		get_msr(msr, lo, hi);
		return ((uint64_t) hi << 32) | lo;
	}

	/**
	 * \brief Write model-specific register
	 */
	static forceinline void set_msr(uint32_t msr, uint32_t lo, uint32_t hi) {
		asm volatile("wrmsr" : : "a"(lo), "d"(hi), "c"(msr));
	}

	/**
	 * \brief Write model-specific register
	 */
	static forceinline void set_msr(uint32_t msr, uint64_t val) {
		uint32_t lo = val & 0xFFFFFFFF;
		uint32_t hi = val >> 32;

		set_msr(msr, lo, hi);
	}
};

#define __asm_label(a) #a
#define _asm_label(a) __asm_label(a)
#define asm_label(label) asm volatile (".asm_label." label "_%=:" :: "m" (*(void *)0))

#endif // __MACHINE_H__
