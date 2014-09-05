/**
 * @file
 * @ingroup ARM
 * @brief Serial driver implementation
 */
#include "serial.h"
#include "platform.h"

#define SERIAL_FLAG_REGISTER 0x18
#define SERIAL_BUFFER_FULL (1 << 5)

Serial::Serial() {
	// nothing to do
}

void Serial::putchar(char character) {
    // wait while transmit full
    bool full;
    do {
        full = *(volatile unsigned long*)(SERIAL_BASE + SERIAL_FLAG_REGISTER) & (SERIAL_BUFFER_FULL);
    } while(full);

    // put our character, c, into the serial buffer
    *(volatile unsigned long*) SERIAL_BASE = character;
}

void Serial::puts(const char* data) {
	while(*data) putchar(*data++);
}
