#ifndef __TERMINAL_H__
#define __TERMINAL_H__

/**
 * @file
 *
 * @ingroup i386
 *
 * \brief CGA output
 */

#include <stddef.h>
#include <stdint.h>
#include "arch/generic/ostream.h"

class CGA : public O_Stream {
	static const size_t WIDTH = 80;
	static const size_t HEIGHT = 24;

	static uint16_t* const BUFFER;
	
	size_t row;
	size_t column;
	uint8_t color;

protected:
	uint16_t vgaentry(char c, uint8_t color);
	void check_bounds();
	void scroll();

public:
	/** CGA colors */
	enum color {
		BLACK = 0,
		BLUE = 1,
		GREEN = 2,
		CYAN = 3,
		RED = 4,
		MAGENTA = 5,
		BROWN = 6,
		LIGHT_GREY = 7,
		DARK_GREY = 8,
		LIGHT_BLUE = 9,
		LIGHT_GREEN = 10,
		LIGHT_CYAN = 11,
		LIGHT_RED = 12,
		LIGHT_MAGENTA = 13,
		LIGHT_BROWN = 14,
		WHITE = 15,
	};

	CGA();

	void clear();

	void setcolor(enum color fg, enum color bg);

	void putentryat(char c, uint8_t color, size_t x, size_t y);

	void putchar(char c);

	void puts(const char* data);
};


#endif
