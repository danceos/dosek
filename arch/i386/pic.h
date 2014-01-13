/**
 * @file
 * @ingroup i386
 * @brief i386 Programmable Interrupt Controller (PIC)
 */

#ifndef PIC_H_
#define PIC_H_

#include "stdint.h"
#include "ioport.h"

namespace arch {

/** \brief Programmable Interrupt Controller (PIC) */
class PIC {
	enum {
		PIC1 = 0x20, //!< IO base address for master PIC
		PIC2 = 0xA0, //!< IO base address for slave PIC
		PIC1_COMMAND = PIC1,
		PIC1_DATA = PIC1+1,
		PIC2_COMMAND = PIC2,
		PIC2_DATA = PIC2+1,
		PIC_EOI = 0x20 //!< End-of-interrupt command code
	};

public:
	/** \brief Initialize the PIC */
	static void init();

	/** \brief Remap PIC interrupt vectors
	 *
	 * reinitialize the PIC controllers, giving them specified vector offsets
	 * rather than 0x08 and 0x70, as configured by default
	 *
	 * \param offset1 vector offset for master PIC (offset1..offset1+7)
	 * \param offset2 vector offset for for slave PIC (offset2..offset2+7)
	 */
	static void remap(uint8_t offset1, uint8_t offset2);

	/** \brief Disable interrupt delivery from PIC */
	static void disable();

	/** \brief Send end-of-interrupt signal
	 *
	 * \param irq Acknowledged IRQ number (original, not remapped value) */
	static inline void sendEOI(uint8_t irq) {
		if(irq >= 8)
			outb(PIC2_COMMAND, PIC_EOI);

		outb(PIC1_COMMAND, PIC_EOI);
	}
};

}

#endif /* PIC_H_ */
