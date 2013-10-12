#ifndef __SERIAL_H__
#define __SERIAL_H__

/**
 * @file
 *
 * @ingroup i386
 *
 * \brief RS232 driver
 */

#include <stddef.h>
#include <stdint.h>
#include "arch/generic/ostream.h"

class Serial : public O_Stream {
	uint16_t const PORT;

public:
	/** COM ports */
	enum ports {
		COM1 = 0x03f8,
		COM2 = 0x02f8,
		COM3 = 0x03e8,
		COM4 = 0x02e8
	};

	Serial(ports port);

	void putchar(char c);

	void puts(const char* data);
};

#endif // __SERIAL_H__
