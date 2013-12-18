/**
 * @file
 * @ingroup i386
 * @brief i386 Interrupt Descriptor Table (IDT) structures
 */

#ifndef IDT_H_
#define IDT_H_

#include "stdint.h"

namespace arch {

/** \brief IDT descriptor/entry */
class IDTDescriptor {
public:
	union {
		struct {
			uint16_t offset_1;
			uint16_t selector;
			uint8_t  zero;
			uint8_t  type_attr;
			uint16_t offset_2;
		} __attribute__((packed));

		uint64_t value; //!< raw descriptor contents
	} __attribute__((packed));

	/** \brief Constructor for empty descriptor */
	constexpr IDTDescriptor() : value(0) {};

	/** \brief Constructor for IDT descriptor */
	constexpr IDTDescriptor(uint32_t handler, uint16_t sel, uint8_t type) :
		offset_1(handler & 0x0000FFFF),
		selector(sel),
		zero(0),
		type_attr(type),
		offset_2(handler >> 16) {};
} __attribute__((packed));



/** \brief IDT register structure for `lidt` instruction */
struct InterruptDescriptorTable {
	uint16_t limit; //!< IDT size in bytes
	const IDTDescriptor* base; //!< IDT base address
} __attribute__((packed));



/** \brief Global IDT interface */
class IDT {
	/** \brief the actual IDT (array of descriptors) */
	static const IDTDescriptor descriptors[];

	/** \brief IDT register value */
	static const InterruptDescriptorTable idt;

	/** \brief Gate types */
	enum {
		TYPE_DPL0_IRQ_GATE = 0x8E,
		TYPE_DPL0_TRAP_GATE = 0x8F,
		TYPE_DPL3_IRQ_GATE = 0xEE
	};

public:
	/** \brief Initialize and enable the IDT */
	static void	init();
};

}

#endif /* IDT_H_ */
