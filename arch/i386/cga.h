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


/** \brief CGA Colors */
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


extern "C" uint16_t cga_buffer;


class CGA : public O_Stream<CGA> {
	static const size_t WIDTH = 80;
	static const size_t HEIGHT = 24;

	static constexpr uint16_t* const &BUFFER = &cga_buffer;

	static size_t row;
	static size_t column;
	uint8_t color;

protected:
	uint16_t vgaentry(char c, uint8_t color);
	void check_bounds();
	void scroll();

public:
	CGA();

	void clear();

	void setcolor(Color fg, Color bg);

	void putentryat(char c, uint8_t color, size_t x, size_t y);

	void putchar(char c);

	void puts(const char* data);
};


#endif
