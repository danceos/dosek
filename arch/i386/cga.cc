/**
 * @file
 * @ingroup i386
 * @brief CGA output
 */
#include "cga.h"

uint16_t* const CGA::BUFFER = reinterpret_cast<uint16_t*>(0xB8000);

CGA::CGA() {
	setcolor(Color::WHITE, Color::BLACK);
	clear();
}

void CGA::clear() {
	row = column = 0;

	for(size_t y = 0; y < HEIGHT; y++) {
		for(size_t x = 0; x < WIDTH; x++) {
			putentryat(' ', color, x, y);
		}
	}
}

uint16_t CGA::vgaentry(char character, uint8_t color) {
	uint16_t c16 = character;
	uint16_t color16 = color;
	return c16 | color16 << 8;
}

void CGA::setcolor(Color foreground, Color background) {
	color = static_cast<uint8_t>(foreground) | static_cast<uint8_t>(background) << 4;
}

void CGA::putentryat(char character, uint8_t color, size_t x_coord, size_t y_coord) {
	const size_t index = y_coord * WIDTH + x_coord;
	BUFFER[index] = vgaentry(character, color);
}

void CGA::check_bounds() {
	if(column >= WIDTH ) {
		column = 0;
		row++;
	}
	if(row >= HEIGHT) {
		scroll();
		row = HEIGHT-1;
		column = 0;
	}
}

void CGA::scroll() {
	// move lines up
	for(unsigned int i=0; i<WIDTH*HEIGHT; i++) {
		BUFFER[i] = BUFFER[i + WIDTH];
	}

	// clear last line
	for(unsigned int i=0; i<WIDTH; i++) {
		putentryat(' ', 0x0000, i, HEIGHT-1);
	}
}

void CGA::putchar(char character) {
	switch(character) {
	case '\n':
		column = 0;
		row++;
		check_bounds();
		break;

	case '\t':
		while(++column % 8) {
			putentryat(' ', color, column, row);
			check_bounds();
		}
		break;

	case '\b':
		if(column > 0) {
			column--;
		} else {
			row--;
			column = WIDTH;
		}
		putentryat(' ', color, column, row);
		break;

	default:
		putentryat(character, color, column, row);
		column++;
		check_bounds();
        break;
	}
}

void CGA::puts(const char* data) {
	while(*data) putchar(*data++);
}
