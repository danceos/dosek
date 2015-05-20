/**
 * @file
 * @ingroup i386
 * @brief Multiprocessor bootup
 */

#ifndef MP_H_
#define MP_H_

#include "ioport.h"
#include "lapic.h"
#include "stdint.h"
#include "paging.h"

extern "C" char mp_setup;
extern "C" char mp_setup_end;

extern "C" void *mp_stack;
extern "C" volatile int cpu_started;
extern void(* volatile mp_startup_function)();

namespace arch {

/** Loops some time to be able to wait a bit. Uses PIT to determine the time. */
static void boot_delay(unsigned int amount) {
	for (unsigned int i = 0; i < amount; ++i) {
		unsigned int curr_count, prev_count = ~0;
		int delta;

		/* Write to the PIT's mode register that it should make
		 * a snapshot of the current value which is read afterwards
		 * from the channel 0 register while it continues counting. */
		outb(0x43, 0);                /* Set mode register accordingly */
		curr_count = inb(0x40);       /* Read lower counter byte */
		curr_count |= inb(0x40) << 8; /* Read upper counter byte */

		do {
			prev_count = curr_count;

			/* The same as above: Read current value. */
			outb(0x43, 0);
			curr_count = inb(0x40);
			curr_count |= inb(0x40) << 8;
			delta = curr_count - prev_count;

			/* From the linux 2.4 source code:
			 * (https://www.kernel.org/pub/linux/kernel/people/marcelo/linux-2.4/arch/i386/kernel/apic.c)
			 *
			 * This limit for delta seems arbitrary, but it isn't, it's
			 * slightly above the level of error a buggy Mercury/Neptune
			 * chipset timer can cause.
			 */
		} while (delta < 300);
	}
}

/** Boots the cpu with the specified LAPIC-ID. The booted cpu will use
    top_of_stack as the initial stack register. */
bool boot_cpu(unsigned int cpu_id, void *bottom_of_stack,
              unsigned int size_of_stack, void(*startup_function)()) {

	/* Disable paging while starting the second cpu.
	 * Reason: Require write access to the BIOS area for the reset vector and to
	 *         0x40000 where the relocated mp_setup code is copied. */
#ifdef CONFIG_ARCH_MPU
	bool mmu_enabled = MMU::disable();
#endif

	/* Set variables to communicate with the application cpu */
	mp_stack = reinterpret_cast<void *>(reinterpret_cast<unsigned int>(bottom_of_stack) + size_of_stack);
	cpu_started = 0;
	mp_startup_function = startup_function;

	/* Move mp_startup to appropriate location. (Same as in MPStuBS)
	 * This is required for the STARTUP IPI */
	char *relocated_mp_setup = reinterpret_cast<char *>(0x40000);
	unsigned long mp_size = (&mp_setup_end) - (&mp_setup);

	for (unsigned long i = 0; i < mp_size; ++i) {
		/* Avoid memcpy optimization (which would lead to external linkage) */
		asm volatile ("":::);
		*(relocated_mp_setup + i) = *((&mp_setup) + i);
	}

	/* INIT IPI */
	/* -------- */

	/* Prepare BIOS warm reset: Jump to mp_startup */
	outb(0x70, 0xf);
	outb(0x71, 0xa);
	*reinterpret_cast<volatile uint32_t *>(0x467) = reinterpret_cast<uint32_t>(relocated_mp_setup);

	/* Send assert INIT */
	LAPIC::trigger_IPI(0, 5, 0, 1, 1, 0, cpu_id);

	boot_delay(2);

	/* Send deassert INIT */
	LAPIC::trigger_IPI(0, 5, 0, 0, 1, 2, cpu_id);

	/* STARTUP IPI */
	/* ----------- */

	bool pendingIPI = true;
	uint32_t timeout = 0;

	/* Only required on new chips */
	if (!LAPIC::is_external_APIC()) {
		/* Send up to three IPIs */
		for (int j = 0; j < 2; ++j) {
			LAPIC::trigger_IPI(reinterpret_cast<unsigned long>(relocated_mp_setup) >> 12, 6, 0, 0, 0, 0, cpu_id);

			do {
				boot_delay(1);
				++timeout;
				pendingIPI = LAPIC::is_IPI_pending();
			} while (pendingIPI && timeout < 10);

			if (!pendingIPI) {
				break;
			}
		}
	}

	if (!pendingIPI) {
		/* Wait for cpu to report back */
		while (!cpu_started && timeout++ < 10000)
			boot_delay(1);
	}
#ifdef CONFIG_ARCH_MPU
	/* Only restart the MMU if it was previously used! */
	if (mmu_enabled)
		MMU::enable();
#endif

	return cpu_started;
}

}

#endif
