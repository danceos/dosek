/**
 * @file
 * @ingroup i386
 * @brief i386 MMU/Paging structures
 */

#ifndef PAGING_H_
#define PAGING_H_

#include "stdint.h"

namespace arch {

/** \brief Page table entry describing one 4 KB page */
class PageTableEntry {
public:
	union {
		struct {
			uint8_t flags;
			uint8_t page_addr0;
			uint16_t page_addr1;
		} __attribute__((packed));

		uint32_t value;
	} __attribute__((packed));

	/** \brief Constructor for one 4 KB page */
	constexpr PageTableEntry(uint32_t page_addr, bool rw = true, bool usermode = false) :
		flags((1 << 6) | (1 << 5) | (usermode<<2) | (rw<<1) | 0x1),
		page_addr0((page_addr & 0x0000F000) >> 8),
		page_addr1(page_addr >> 16)
		{};

	/** \brief Constructor for empty entry */
	constexpr PageTableEntry() : value(0) {};
} __attribute__((packed));



/** \brief Page table containing 1024 page table entries */
class PageTable {
	PageTableEntry entries[1024] __attribute__ ((aligned (4096)));
};



/** \brief Page directory entry referencing one page table */
class PageDirectoryEntry {
public:
	union {
		struct {
			uint8_t flags;
			uint8_t page_table_addr0;
			uint16_t page_table_addr1;
		} __attribute__((packed));

		uint32_t value;
	} __attribute__((packed)); 

	/** \brief Constructor for one page table entry */
	constexpr PageDirectoryEntry(uint32_t page_table_addr, bool rw = true, bool usermode = true) :
		flags((1 << 6) | (1 << 5) | (usermode<<2) | (rw<<1) | 0x1),
		page_table_addr0((page_table_addr & 0x0000F000) >> 8),
		page_table_addr1(page_table_addr >> 16)
		{};

	/** \brief Constructor for empty entry */
	constexpr PageDirectoryEntry() : value(0) {};
} __attribute__((packed));



/** \brief Page directory containing 1024 page directory entries */
class PageDirectory {
	PageDirectoryEntry entries[1024] __attribute__ ((aligned (4096)));

public:
	/** \brief Enable/use this page directory by loading its address into CR3 register */
	void enable(void) const;
};



/** \brief  Global MMU/paging API */
class MMU {
public:
	/** \brief Initialize and enable paging */
	static void init();
};

}

#endif /* PAGING_H_ */
