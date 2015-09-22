#ifndef __MACHINE_H__
#define __MACHINE_H__


#include "os/util/inline.h"
#include "csr.h"

/**
 *  @ingroup arch
 *  @defgroup posix Posix "Hardware" abstraction
 *  @brief Architecture specific code for the posix "hardware".
 */

/**
 * @file
 *
 * @ingroup osek-v
 *
 * @brief Machine dependent special instructions.
 */

#include <stdint.h>

class Machine
{
public:
	static unsigned char soft_irq_cause;

    static void init(void) {
    }

	/**
	 * \brief Emits a nop opcode. (nop)
	 */
	static forceinline void nop(void) {
		asm volatile ("nop");
	};

	/**
	 * \brief Emits an undefined instruction trap.
	 * Used for runtime asserts.
	 */
	static forceinline void debug_trap(void) {
	}

	/**
	 * \brief Disable all interrupts
	 */
	static forceinline bool disable_interrupts() {
		return clear_csr_bit(mstatus, MSTATUS_IE);
    }

	/**
	 * \brief Enable all interrupts
	 */
	static forceinline void enable_interrupts() {
		set_csr_bit(mstatus, MSTATUS_IE);
    }

	/**
	 * \brief Enable all interrupts
	 */
	static forceinline void set_sp(const void* sp) {
		asm volatile ("mv sp, %0" :: "r"(sp) : "memory");
    }

	/**
	 * \brief Return if interrupts are enabled
	 */
	static forceinline bool interrupts_enabled(void) {
		return get_csr_bit(mstatus, MSTATUS_IE);
	}

	/**
	 * \brief Unreachable code
	 * Will trigger interrupt if this is actually executed.
	 */
	static noinline void unreachable(void) {
		__builtin_unreachable(); // allow compiler optimization
	}


	/**
	 * \brief Shutdown machine using ACPI
	 * The static ACPI values used work for QEMU and Bochs but probably not on real PCs!
	 */
	static forceinline void shutdown(void) {
		do { write_csr(mtohost, 1); } while(1);
	}

	static forceinline void * exchange_saved_ip(unsigned id, void *pc) {
		void *ret;
		asm volatile ("osek.ld %0, %1, %2;" : "=r"(ret) : "r"(pc), "r"(id));
		return ret;
	}

	static forceinline unsigned syscall(const unsigned number) {
		unsigned ret;
		asm volatile ("osek %0, %1" : "=r"(ret) : "I"(number));
		return ret;
	}


	/**
	 * \brief Trigger an interrupt
	 */
	static forceinline void trigger_interrupt(uint8_t irq_) {
		bool interrupts = disable_interrupts();
		soft_irq_cause = irq_;
		set_csr_bit(mip, MIP_MSIP);
		if (interrupts)
			enable_interrupts();
	}
	static forceinline void trigger_interrupt_from_user(uint8_t irq_) {
		trigger_interrupt(irq_);
	}

	static forceinline uint64_t read_csr(unsigned reg) {
		uint64_t __ret;
		asm volatile ("csrr %0, %1" : "=r"(__ret) : "i"(reg));
		return __ret;
	}

	static forceinline void write_csr(unsigned reg, uint64_t val) {
		asm volatile ("csrw %0, %1" :: "i"(reg), "r"(val));
	}

	static forceinline uint64_t swap_csr(unsigned reg, uint64_t val) {
		uint64_t __ret;
		asm volatile ("csrrw %0, %1, %2" : "=r"(__ret) : "i"(reg), "r"(val));
		return __ret;
	}

	static forceinline bool get_csr_bit(unsigned reg, uint8_t bit) {
		uint64_t csr = read_csr(reg);
		return csr & (1 << bit);
	}

	static forceinline bool set_csr_bit(unsigned reg, uint8_t bit) {
		bool __ret;
		if (__builtin_constant_p(bit) && (bit) < 32)
			asm volatile ("csrrs %0, %1, %2" : "=r"(__ret) : "i"(reg), "i"(bit));
		else
			asm volatile ("csrrs %0, %1, %2" : "=r"(__ret) : "i"(reg), "r"(bit)); \
		return __ret;
	}

	static forceinline bool clear_csr_bit(unsigned reg, uint8_t bit) {
		bool __ret;
		if (__builtin_constant_p(bit) && (bit) < 32)
			asm volatile ("csrrc %0, %1, %2" : "=r"(__ret) : "i"(reg), "i"(bit));
		else
			asm volatile ("csrrc %0, %1, %2" : "=r"(__ret) : "i"(reg), "r"(bit)); \
		return __ret;
	}


	static forceinline void sync() {
		asm volatile ("fence");
	}
};

#define __asm_label(a) #a
#define _asm_label(a) __asm_label(a)
// #define asm_label(label) asm volatile (".asm_label." label "_%=:" :: "m" (*(void *)0))
#define asm_label(label)


#endif // __MACHINE_H__
