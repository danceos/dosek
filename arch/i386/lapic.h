/**
 * @file
 * @ingroup i386
 * @brief i386 Local Advanced Programmable Interrupt Controller (local APIC)
 */

#ifndef LAPIC_H_
#define LAPIC_H_

#include "stdint.h"
#include "ioport.h"
#include "os/util/inline.h"

namespace arch {

/** \brief Local Advanced Programmable Interrupt Controller (local APIC) */
class LAPIC {
	enum lapic_reg {
		BASE = 0xFEE00000, //!< base address for LAPIC
		ID = BASE + 0x020, //!< local APIC ID register
		VER = BASE + 0x030, //!< local APIC version register
		SINT = BASE + 0x0F0, //!< spurious interrupt register
		TPR = BASE + 0x080, //!< task priority register
		PPR = BASE + 0x0A0, //!< processor priority register
		EOI = BASE + 0x0B0, //!< end-of-interrupt register
		IRR = BASE + 0x200, //!< interrupt request register
		ESR = BASE + 0x280, //!< error status register
		ISR = BASE + 0x100, //!< in-service register
		ICR_LO = BASE + 0x0300, //!< interrupt control register, bits 0-31
		ICR_HI = BASE + 0x0310, //!< interrupt control register, bits 32-63
	};

	static forceinline void write_reg(lapic_reg reg, uint32_t val) {
		*((volatile uint32_t*) reg) = val;
	}

	static forceinline uint32_t read_reg(lapic_reg reg) {
		return *((volatile uint32_t*) reg);
	}

public:
	/** \brief Initialize the LAPIC */
	static void init();

	/** \brief Enable local APIC */
	static forceinline void enable() {
		uint32_t val = read_reg(SINT);
		val |= 0x100; // enable APIC bit
		write_reg(SINT, val);
	}

	/** \brief Send end-of-interrupt signal */
	static forceinline void send_eoi() {
		write_reg(EOI, 0);
	}

	/** \brief Return local APIC ID */
	static forceinline uint8_t get_id() {
		return read_reg(ID);
	}

	/** \brief Return interrupt request register */
	static forceinline uint32_t get_irr(uint8_t offset) {
		return read_reg((lapic_reg) (IRR + (offset)*0x10));
	}

	/** \brief Return interrupt service register */
	static forceinline uint32_t get_isr(uint8_t offset) {
		return read_reg((lapic_reg) (ISR + (offset)*0x10));
	}

	/** \brief Set task priority
	 *
	 * This will block all IRQ vectors lower than the given priority.
	 */
	static forceinline void set_task_prio(uint8_t prio) {
		write_reg(TPR, prio);
	}

	/** \brief Return task priority */
	static forceinline uint8_t get_task_prio() {
		return static_cast<uint8_t>(read_reg(TPR));
	}

	/** \brief Return processor interrupt priority */
	static forceinline uint8_t get_processor_prio() {
		return static_cast<uint8_t>(read_reg(PPR));
	}

	/** \brief Trigger interrupt vector */
	static forceinline void trigger(uint8_t vector) {
		// write interrupt vector
		// fixed delivery mode
		// physical destination mode
		// assert level
		// destination shorthand: self
		write_reg(ICR_LO, (1 << 18) | (1<<14) | vector);
	}

	/** \brief Trigger NMI */
	static forceinline void trigger_NMI() {
		// NMI delivery mode
		// physical destination mode
		// assert level
		// destination shorthand: self
		write_reg(ICR_LO, (1 << 18) | (1<<14) | (4 << 8));
	}

	/** \brief Trigger IPI. Parameters are unchecked! */
	static forceinline void trigger_IPI(uint32_t vector,
	                                    uint32_t delivery_mode,
	                                    uint32_t destination_mode,
	                                    uint32_t level,
	                                    uint32_t trigger_mode,
	                                    uint32_t destination_shorthand,
	                                    uint32_t destination) {
		write_reg(ICR_HI, (destination << (32 - 8)));
		write_reg(ICR_LO, (destination_shorthand << 18) |
		                  (trigger_mode << 15) |
		                  (level << 14) |
		                  (destination_mode << 11) |
		                  (delivery_mode << 8) |
		                  vector);
	}

	/** \brief Return if there is a pending IPI */
	static forceinline bool is_IPI_pending() {
		return read_reg(ICR_LO) & (1 << 12);
	}

	/** \brief Return if the APIC is an external chip */
	static forceinline bool is_external_APIC() {
		return (read_reg(VER) & 0xf0) == 0x00;
	}
};

}

#endif /* LAPIC_H_ */
