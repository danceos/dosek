/**
 * @file
 * @ingroup i386
 * @brief i386 MMU/Paging setup
 */

#include "paging.h"

namespace arch {

/** OS/kernel page directory used during syscalls and startup */
extern "C" const __attribute__((weak)) __attribute__((section(".paging"))) PageDirectory pagedir_os;

void MMU::init() {
	// enable the OS page directory
	pagedir_os.enable();

	// enable paging and write protection in CR0
	unsigned int cr0;
	asm volatile("mov %%cr0, %0": "=b"(cr0));
	cr0 |= 0x80010000;
	asm volatile("mov %0, %%cr0":: "b"(cr0));
}

void PageDirectory::enable(void) const {
	// load directory address in CR3
	asm volatile("mov %0, %%cr3":: "b"(entries));
}

}
