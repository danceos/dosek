/**
 * @file
 * @ingroup i386
 * @brief i386 Programmable Interrupt Controller (PIC)
 */

#include "pic.h"

namespace arch {

void PIC::remap(uint8_t offset1, uint8_t offset2)
{
	// save masks
	uint8_t mask1 = inb(PIC1_DATA);
	uint8_t mask2 = inb(PIC2_DATA);

	// start the initialization sequence (in cascade mode)
	outb(PIC1_COMMAND, 0x11);
	io_wait();
	outb(PIC2_COMMAND, 0x11);
	io_wait();

	// set vector offsets
	outb(PIC1_DATA, offset1);
	io_wait();
	outb(PIC2_DATA, offset2);
	io_wait();

	// tell Master PIC that there is a slave PIC at IRQ2 (0000 0100)
	outb(PIC1_DATA, 4);
	io_wait();
	// tell Slave PIC its cascade identity (0000 0010)
	outb(PIC2_DATA, 2);
	io_wait();

	// set 8086/88 (MCS-80/85) mode
	outb(PIC1_DATA, 0x01);
	io_wait();
	outb(PIC2_DATA, 0x01);
	io_wait();

	// restore masks
	outb(PIC1_DATA, mask1);
	outb(PIC2_DATA, mask2);
}

void PIC::disable() {
	outb(PIC1_DATA, 0xFF);
	outb(PIC2_DATA, 0xFF);
}

void PIC::init() {
	// remap interrupts to avoid conflicts
	remap(0x20, 0x28);

	// TODO: disable PIC when using APIC
	//disable();
}

}; // namespace arch
