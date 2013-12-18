/**
 * @file
 * @ingroup i386
 * @brief i386 Global Descriptor Table (GDT) structures
 */

#ifndef GDT_H_
#define GDT_H_

#include "stdint.h"

namespace arch {

/** \brief Task State Segment entry */
struct tss_entry {
   uint32_t prev_tss;
   uint32_t esp0;	//!< kernel stack pointer
   uint32_t ss0;	//!< kernel stack segment index
   uint32_t esp1;
   uint32_t ss1;
   uint32_t esp2;
   uint32_t ss2;
   uint32_t cr3;
   uint32_t eip;
   uint32_t eflags;
   uint32_t eax;
   uint32_t ecx;
   uint32_t edx;
   uint32_t ebx;
   uint32_t esp;
   uint32_t ebp;
   uint32_t esi;
   uint32_t edi;
   uint32_t es;
   uint32_t cs;
   uint32_t ss;
   uint32_t ds;
   uint32_t fs;
   uint32_t gs;
   uint32_t ldt;
   uint16_t trap;
   uint16_t iomap_base;
} __attribute__((packed));



/** \brief GDT descriptor/entry */
class GDTDescriptor {
public:
	union {
		struct {
			uint16_t segment_limit0;
			uint16_t base0;
			uint8_t  base1;
			uint8_t  flags;
			uint8_t  segment_limit1;
			uint8_t  base2;
		} __attribute__((packed));

		uint64_t value; //!< raw descriptor contents
	} __attribute__((packed));

	/** \brief Constructor for empty descriptor */
	constexpr GDTDescriptor() : value(0) {};

	/** \brief Constructor for directly given value */
	constexpr GDTDescriptor(uint64_t val) : value(val) {};

	/** \brief Constructor for GDT descriptor */
	constexpr GDTDescriptor(uint32_t base, uint32_t limit, bool code, bool user) :
		segment_limit0(((limit > 0xFFFF) ? limit>>12 : limit) & 0x0000FFFF),
		base0(base & 0x0000FFFF),
		base1((base & 0x00FF0000) >> 16),
		flags((user ? 0xF0 : 0x90) | (code ? 0x0B : 0x03)), // present, non-system, DPL 0/3, code/data, accessed
		segment_limit1(((limit > 0xFFFF) ? 0xC0 : 0x40) | (((limit > 0xFFFF) ? limit>>12 : limit) & 0x000F0000) >> 16),
		base2((base & 0xFF000000) >> 24) {};

	/** \brief Constructor for TSS descriptor */
	constexpr GDTDescriptor(uint32_t tss_base, uint32_t tss_size) :
		segment_limit0((tss_size) & 0x0000FFFF),
		base0(tss_base & 0x0000FFFF),
		base1((tss_base & 0x00FF0000) >> 16),
		flags(0x80 | 0x09), // present, system, DPL0, TSS (TODO: DPL3?)
		segment_limit1(0x40 | (tss_size & 0x000F0000) >> 16),
		base2((tss_base & 0xFF000000) >> 24) {};
} __attribute__((packed));



/** \brief GDT register structure for `lgdt` instruction */
struct GlobalDescriptorTable {
	uint16_t limit; //!< GDT size in bytes
	const GDTDescriptor* base; //!< GDT base address
} __attribute__((packed));



/**\brief  Global GDT interface */
class GDT {
	/** \brief the actual GDT (array of descriptors) */
	static const GDTDescriptor descriptors[];

	/** \brief GDT register value */
	static const GlobalDescriptorTable gdt;

public:
	/** \brief Static GDT descriptor offsets */
	enum {
		KERNEL_CODE_SEGMENT = 0x8,
		KERNEL_DATA_SEGMENT = 0x10,
		USER_CODE_SEGMENT = 0x18,
		USER_DATA_SEGMENT = 0x20,
		TSS_SEGMENT = 0x28
	};

	/** \brief Initialize and enable the GDT */
	static void init();
};

}

#endif /* GDT_H_ */
