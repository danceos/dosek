#include "serial.h" 
#include "ioport.h"

Serial::Serial(ports port) : PORT((uint16_t) port) {
	outb(PORT + 1, 0x00);    // Disable all interrupts
	outb(PORT + 3, 0x80);    // Enable DLAB (set baud rate divisor)
	outb(PORT + 0, 0x03);    // Set divisor to 3 (lo byte) 38400 baud
	outb(PORT + 1, 0x00);    //                  (hi byte)
	outb(PORT + 3, 0x03);    // 8 bits, no parity, one stop bit
	outb(PORT + 2, 0xC7);    // Enable FIFO, clear them, with 14-byte threshold
	outb(PORT + 4, 0x0B);    // IRQs enabled, RTS/DSR set
}

void Serial::putchar(char character) {
    // wait while transmit not empty
    bool empty;
    do {
        empty = (inb(PORT + 5) & 0x20);
    } while(!empty);

	outb(PORT, character);
}

void Serial::puts(const char* data) {
	while(*data) putchar(*data++);
}
