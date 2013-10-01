#include "cga.h" 

uint16_t* const CGA::BUFFER = reinterpret_cast<uint16_t*>(0xB8000);

CGA::CGA() {
	setcolor(LIGHT_GREY, BLACK);
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

uint16_t CGA::vgaentry(char c, uint8_t color) {
	uint16_t c16 = c;
	uint16_t color16 = color;
	return c16 | color16 << 8;
}

void CGA::setcolor(enum color fg, enum color bg) {
	color = fg | bg << 4;
}

void CGA::putentryat(char c, uint8_t color, size_t x, size_t y) {
	const size_t index = y * WIDTH + x;
	BUFFER[index] = vgaentry(c, color);
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

void CGA::putchar(char c) {
	switch(c) {
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
		putentryat(c, color, column, row);
		column++;
		check_bounds();
	}
}

void CGA::puts(const char* data) {
	while(*data) putchar(*data++);
}
