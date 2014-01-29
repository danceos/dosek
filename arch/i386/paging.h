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
	/** \brief Enable/use page directory by loading its address into CR3 register */
	static inline void enable(PageDirectory &pagedir) {
		// load directory address in CR3
		asm volatile("mov %0, %%cr3":: "r"(pagedir.entries));
	}

	/** \brief Enable/use page directory by loading its address into CR3 register */
	static inline void enable(const PageDirectoryEntry pagedir[]) {
		enable(*(PageDirectory *) pagedir);
	}
};



/**
 * @name Page directories
 * @{
 */
/** \brief OS/kernel page directory used during syscalls and startup */
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_os[1024];

// TODO: generate task directory declarations
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task1[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task2[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task3[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task4[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task5[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task6[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task7[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task8[1024];
/**@}*/

/** \brief Array of task page directories */
// horrible C++ type declarations ...
constexpr const PageDirectoryEntry (* const pagedirs[])[1024] = {
	&pagedir_os,
	&pagedir_task1,
	&pagedir_task2,
	&pagedir_task3,
	&pagedir_task4,
	&pagedir_task5,
	&pagedir_task6,
	&pagedir_task7,
	&pagedir_task8
};



/** \brief  Global MMU/paging API */
class MMU {
public:
	/** \brief Initialize and enable paging */
	static void init();

	/** \brief Switch to page directory of specific task */
	static inline void switch_task(uint32_t id) {
		PageDirectory::enable(*pagedirs[id]);
	}
};

}

#endif /* PAGING_H_ */
