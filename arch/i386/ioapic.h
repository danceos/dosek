/**
 * @file
 * @ingroup i386
 * @brief i386 I/O Advanced Programmable Interrupt Controller (IO APIC)
 */

#ifndef IOAPIC_H_
#define IOAPIC_H_

#include "stdint.h"
#include "lapic.h"
#include "ioport.h"

namespace arch {

/** \brief I/O Programmable Interrupt Controller (IOAPIC) */
class IOAPIC {
	enum ioapic_reg {
		BASE = 0xFEC00000, //!< base address for IOAPIC
		IOREGSEL = BASE + 0, //!< register select register
		IOWIN = BASE + 0x10, //!< I/O window register
		IOREDTBL = 0x10 //!< start of I/O redirection table
	};

	static inline void write_reg(uint8_t reg, uint32_t val) {
		*((volatile uint32_t*) IOREGSEL) = reg;
		*((volatile uint32_t*) IOWIN) = val;
	}

	static inline uint32_t read_reg(uint8_t reg) {
		*((volatile uint32_t*) IOREGSEL) = reg;
		return *((volatile uint32_t*) IOWIN);
	}

public:
	/** \brief Interrupt delivery mode */
	enum delivery_mode {
		FIXED, //!< deliver on the INTR signal of all destination processors
		LOWEST_PRIORITY, //!< deliver to lowest-priority destination CPU
		SMI, //!< system management interrupt (vector ignored)
		NMI = 4, //!< non-maskable interrupt (vector ignored)
		INIT, //!< perform INIT at destination processors (vector ignored)
		EXTINT = 7 //!< deliver as an external (PIC) interrupt on all destination processors
	};

	/** \brief Initialize the IOAPIC */
	static void init();

	/** \brief Setup interrupt (redirection)
	 *
	 * \param pin interrupt pin to configure
	 * \param vector interrupt vector to request at APIC
	 * \param del_mode interrupt delivery mode (default: FIXED)
	 * \param active_low interrupt is active-low? (default: false)
	 */
	static inline void setup_irq(uint8_t pin, uint8_t vector, delivery_mode del_mode = FIXED, bool active_low = false) {
		uint8_t reg_lo = IOREDTBL + pin*2;
		write_reg(reg_lo, (active_low << 13) | (del_mode << 8) | vector);

		// spec says to write destination APIC ID, but it also works without...
		//uint8_t reg_hi = IOREDTBL + pin*2 + 1;
		//write_reg(reg_hi, LAPIC::get_id() << 24);
	}
};

}

#endif /* IOAPIC_H_ */
