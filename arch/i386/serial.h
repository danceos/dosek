#ifndef __SERIAL_H__
#define __SERIAL_H__

/**
 * @file
 *
 * @ingroup i386
 *
 * \brief RS232 driver
 */

#include <stdint.h>
#include "arch/generic/ostream.h"


/** \brief  Colors (just copied from cga), actually not used */
typedef enum class Color {
	BLACK   = 0,
	BLUE    = 1,
	GREEN   = 2,
	CYAN    = 3,
	RED     = 4,
	MAGENTA = 5,
	YELLOW  = 6,
	WHITE  = 15,
} Color;


class Serial : public O_Stream<Serial> {
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

	template<typename T>
	void setcolor(__attribute__((unused)) T fg, __attribute__((unused)) T bg) {};
};

#endif // __SERIAL_H__
