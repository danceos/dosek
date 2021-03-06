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
		// TODO: do not set %cr3
		// currently this is still required to check if running in userspace in idt.S
		//#ifndef MPU_DISABLED
		// load directory address in CR3
		asm volatile("mov %0, %%cr3":: "r"(pagedir.entries) : "memory");
		//#endif
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
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task9[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task10[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task11[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task12[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task13[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task14[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task15[1024];
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectoryEntry pagedir_task16[1024];

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
	&pagedir_task8,
	&pagedir_task9,
	&pagedir_task10,
	&pagedir_task11,
	&pagedir_task12,
	&pagedir_task13,
	&pagedir_task14,
	&pagedir_task15,
	&pagedir_task16,
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

	/** \brief Disables paging (without removing the current page directory
	 *  from the register)
	 *
	 *  \return true if the MMU was previously enabled, false otherwise
	 **/
	static inline bool disable() {
		unsigned int cr0;
		asm volatile("mov %%cr0, %0": "=b"(cr0));
		bool enabled = ((cr0 & 0x80000000) != 0) ? true : false;
		cr0 &= ~0x80000000;
		asm volatile("mov %0, %%cr0":: "b"(cr0));
		return enabled;
	}

	/** \brief Enables paging (without altering the page directory) */
	static inline void enable() {
		unsigned int cr0;
		asm volatile("mov %%cr0, %0": "=b"(cr0));
		cr0 |= 0x80000000;
		asm volatile("mov %0, %%cr0":: "b"(cr0));
	}
};

}

#endif /* PAGING_H_ */
