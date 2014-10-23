#ifndef __MACHINE_H__
#define __MACHINE_H__

#include "os/util/inline.h"
#include "stdint.h"
#include "output.h"

/**
 *  @ingroup arch
 *  @defgroup ARM ARM Hardware
 *  @brief Architecture specific code for the ARM hardware.
 */

/**
 * @file
 *
 * @ingroup ARM
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
	 * \brief Halts the machine. (WFI)
	 */
	static forceinline void halt(void) {
		asm volatile ("wfi");
	}

	/**
	 * \brief Emits an undefined instruction trap.
	 * Used for runtime asserts.
	 */
	static forceinline void debug_trap(uint16_t number=0) {
        // could also add immediate
		asm volatile ("bkpt %0" :: "i"(number));
		__builtin_unreachable();
	}

    // TODO
    static forceinline void syscall(uint8_t number) {
        // ARM mode allows 24bit comment/number, but
        // Thumb mode only 8 bit
        asm volatile ("svc %0" :: "i"(number));
    }

    // TODO
    static forceinline uint32_t get_cpsr() {
        uint32_t r;
        asm("mrs %[ps], cpsr" : [ps]"=r" (r));
        return r;
    }

     // TODO
    static forceinline void set_cpsr(uint32_t r) {
        asm("msr cpsr, %[ps]" : : [ps]"r" (r));
    }

    // TODO
    static forceinline uint32_t get_spsr() {
        uint32_t r;
        asm("mrs %[ps], spsr" : [ps]"=r" (r));
        return r;
    }

     // TODO
    static forceinline void set_spsr(uint32_t r) {
        asm("msr spsr, %[ps]" : : [ps]"r" (r));
    }

	/**
	 * \brief Panic when error is detected
	 *
	 * Triggers non-maskable error interrupt
	 */
	static forceinline void panic(void) {
		// TODO: APIC NMI request instead of software interrupt?
		//asm volatile ("int %0" :: "i"(arch::Exceptions::NMI));
	}

	/**
	 * \brief Push value on stack
	 */
	static forceinline void push(uint32_t val) {
		// try immediate operand first, use register if not possible
		asm volatile("push %0" :: "ir"(val) : "sp");
	}

	/**
	 * \brief Reset all general-purpose registers to 0
	 */
	static forceinline void clear_registers() {
        asm volatile("mov r0, #0" ::: "r0");
        asm volatile("mov r1, #0" ::: "r1");
        asm volatile("mov r2, #0" ::: "r2");
        asm volatile("mov r3, #0" ::: "r3");
        asm volatile("mov r4, #0" ::: "r4");
        asm volatile("mov r5, #0" ::: "r5");
        asm volatile("mov r6, #0" ::: "r6");
        asm volatile("mov r7, #0" ::: "r7");
        asm volatile("mov r8, #0" ::: "r8");
        asm volatile("mov r9, #0" ::: "r9");
        asm volatile("mov r10, #0" ::: "r10");
        asm volatile("mov r11, #0" ::: "r11");
        asm volatile("mov r12, #0" ::: "r12");
	}

	/**
	 * \brief Enable interrupts
	 */
	static forceinline void enable_interrupts() {
        //set_cpsr(get_cpsr() & ~(1 << 7));
        asm volatile("CPSIE i");
        asm volatile("DSB");
        asm volatile("ISB");
	}

    /**
     * \brief Enable fast interrupts
     */
    static forceinline void enable_fast_interrupts() {
        //set_cpsr(get_cpsr() & ~(1 << 6));
        asm volatile("CPSIE f");
    }

	/**
	 * \brief Disable interrupts
	 */
	static forceinline void disable_interrupts() {
        //set_cpsr(get_cpsr() | (1 << 7));
        asm volatile("CPSID i");
        asm volatile("DSB");
        asm volatile("ISB");
	}

    /**
     * \brief Disable fast interrupts
     */
    static forceinline void disable_fast_interrupts() {
        //set_cpsr(get_cpsr() | (1 << 6));
        asm volatile("CPSID f");
    }

    /**
     * \brief ARM processor modes
     */
    enum mode_t {
        USER        = 16,
        FIQ         = 17,
        IRQ         = 18,
        SUPERVISOR  = 19,
        ABORT       = 23,
        UNDEFINED   = 27,
        SYSTEM      = 31
    };

    /**
     * \brief Switch ARM processor mode
     */
    static forceinline void switch_mode(mode_t mode) {
        asm volatile("cps %0" :: "i"(mode) : "lr");
    }

	/**
	 * \brief halt processor atomically
	 */
	static forceinline void goto_sleep() {
        // TODO: enable BOTH irqs and fast irqs?
		asm volatile("cpie if\n\twfi");
	}


	/**
	 * \brief Return interrupt enable status
	 */
	static forceinline bool interrupts_enabled(void) {
		return (get_cpsr() & (1<<7)) == 0;
	}

    /**
     * \brief Return fast interrupt enable status
     */
    static forceinline bool fast_interrupts_enabled(void) {
        return (get_cpsr() & (1<<6)) == 0;
    }

	/**
	 * \brief Trigger a software interrupt
	 *
	 * Trigger a synchronous software interrupt using the int(errupt)
	 * instruction.
	 *
	 */
	static void trigger_interrupt(uint8_t irq);

	/**
	 * \brief Trigger a non-software interrupt
	 *
	 * Trigger an asynchronous interrupt which looks to the system
	 * like a hardware interrupt. This is probably only
	 * useful for tests and debugging.
	 *
	 * On i386 this interrupt is triggered using the local APIC.
	 */
	//static forceinline void trigger_interrupt(uint8_t irq) {
	//  //arch::LAPIC::trigger(irq);
	//}
	static void trigger_interrupt_from_user(uint8_t irq);


	/**
	 * \brief Unreachable code
	 * Will trigger interrupt if this is actually executed.
	 */
	static forceinline void unreachable(void) {
		//asm volatile("int3");
		__builtin_unreachable(); // allow compiler optimization
	}

	/**
	 * \brief Return from interrupt handler
	 */
	static forceinline void return_from_interrupt(void) {
		asm volatile("LDM sp!, {pc}^");
		unreachable();
	}
#if 0
	/**
	 * \brief Exit to ring 3 and continue with given IP and SP
	 */
	static forceinline void sysexit(void* ip, void* sp) {
		// clear unused registers
		//asm volatile("xor %%eax, %%eax" ::: "eax");
		//asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		//asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		//asm volatile("xor %%esi, %%esi" ::: "esi");
		//asm volatile("xor %%edi, %%edi" ::: "edi");

		//asm volatile("sysexit" :: "d"(ip), "c"(sp));
		unreachable();
	}

	/**
	 * \brief Set flags and exit to ring 3 and continue with given IP and SP and IRQs enabled
	 */
	static forceinline void sysexit_with_sti(void* ip, void* sp, uint32_t flags) {
		// clear unused registers
		///asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		//asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		//asm volatile("xor %%esi, %%esi" ::: "esi");
		//asm volatile("xor %%edi, %%edi" ::: "edi");

		// set flags without interrupt enable flag, then use sti to enable IRQs *after* sysexit
		//asm volatile("push %0; popf; xor %%eax, %%eax; sti; sysexit" :: "ia"(flags & ~0x0200), "d"(ip), "c"(sp));
		unreachable();
	}

	/**
	 * \brief Set flags and exit to ring 3 and continue with given IP and SP
	 */
	static forceinline void sysexit(void* ip, void* sp, uint32_t flags) {
		// clear unused registers
		//asm volatile("xor %%ebx, %%ebx" ::: "ebx");
		//asm volatile("xor %%ebp, %%ebp" ::: "ebp");
		//asm volatile("xor %%esi, %%esi" ::: "esi");
		//asm volatile("xor %%edi, %%edi" ::: "edi");

		// set flags without interrupt enable flag, then use sti to enable IRQs *after* sysexit
		//asm volatile("push %0; popf; xor %%eax, %%eax; sysexit" ::
		//			 "ia"(flags), "d"(ip), "c"(sp));
		unreachable();
	}
#endif


    static void reset(void);

	/**
	 * \brief Shutdown machine
	 * Shutdown by doing a soft-reset (use no-reboot in qemu!)
     * At the moment there is no real shutdown sequence.
	 */
	static forceinline void shutdown(void) {
		#if DEBUG
		// don't really shutdown when debugging
		debug << "shutdown requested" << endl;
		#else
        // TODO
		// write EOT on serial console to exit gem5 simulation
		kout << ((char) 0x04);
        Machine::reset();
		#endif

		// No unreachable() here, otherwise the generator will be unhappy!
		// stop in case ACPI shutdown failed
		//halt(); // causes exception when called from ring 3
		// while(true) nop();
	}
};

#define __asm_label(a) #a
#define _asm_label(a) __asm_label(a)
#define asm_label(label) asm volatile (".asm_label." label "_%=:" :: "m" (*(void *)0))

#endif // __MACHINE_H__
