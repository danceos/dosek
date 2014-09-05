/**
 * @file
 * @ingroup i386
 * @brief i386 Global Descriptor Table (GDT) setup
 */

#include "gdt.h"
#include "machine.h"

/** \brief Linker symbol for end of OS stack */
extern "C" uint8_t _estack_os;

namespace arch {

/** \brief Global Task State Segment
 *
 * This structure is used by the CPU to switch to kernel stack when switching
 * from ring 3.
 * C++ mangling is prevented to allow the linker script to put "tss" at the start
 * of RAM region.
 */
extern "C" struct tss_entry tss;



// the static Global Descriptor Table
constexpr GDTDescriptor GDT::descriptors[] __attribute__ ((aligned (8))) = {
	{}, // null descriptor
	{0x0, 0xFFFFFFFF, true, false}, // kernel code
	{0x0, 0xFFFFFFFF, false, false}, // kernel data
	{0x0, 0xFFFFFFFF, true, true}, // user code
	{0x0, 0xFFFFFFFF, false, true}, // user data
	{0x200000, sizeof(struct tss_entry)} // task state segment
};

// the static GDT register
constexpr GlobalDescriptorTable GDT::gdt __attribute__ ((aligned(8))) = {
	sizeof(GDT::descriptors)-1,
	&descriptors[0]
};



void GDT::init() {
	// load static GDT
	asm volatile("lgdt %0" :: "m"(gdt) : "memory");

	// zero TSS
	// manual memset(&tss, 0, sizeof(tss)); (addr is volatile to prevent llvm generating a call to memset ...)
	for(volatile uint32_t* addr = (uint32_t*) &tss; addr < (uint32_t*)&tss+(sizeof(tss)/4); addr++) *addr = 0;

	// prepare TSS
	tss.esp0 = (uint32_t) (&_estack_os - 16);	// TODO: multiple stacks for concurrent irqs?
	tss.ss0 = KERNEL_DATA_SEGMENT;

	// load TSS
	asm volatile("ltr %0" :: "r"((uint16_t)TSS_SEGMENT) : "memory");

	// setup data segments (already for userspace as it does not hurt in kernel mode)
	Machine::set_data_segment(USER_DATA_SEGMENT);

	// setup code segment
	asm volatile("jmp %0, $1f; 1:" :: "i"(KERNEL_CODE_SEGMENT) : "memory");
}

}
