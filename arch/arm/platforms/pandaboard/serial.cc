/**
 * @file
 * @ingroup ARM
 * @brief Serial driver implementation
 */
#include "serial.h"
#include "platform.h"
Serial::Serial() {
	// nothing to do
}

void Serial::putchar(char character) {
    // wait while transmit full
    bool full;
    do {
        full = *(volatile unsigned long*)(SERIAL_BASE + SERIAL_FLAG_REGISTER_OFFSET) & (SERIAL_BUFFER_FULL);
    } while(full);

    // put our character, c, into the serial buffer
    *(volatile unsigned long*) (SERIAL_BASE + SERIAL_TX_OFFSET) = character;
}

void Serial::puts(const char* data) {
	while(*data) putchar(*data++);
}
