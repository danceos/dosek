#ifndef __COLORTERMINAL_H__
#define __COLORTERMINAL_H__

/**
 * @file
 *
 * @ingroup posix
 *
 * \brief Colored output
 */

#include "terminal.h"
#include <stddef.h>
#include <stdint.h>
#include <string>

/** Terminal colors
 */
typedef enum class  Color {
	BLACK    = 0,
	RED      = 1,
	GREEN    = 2,
    YELLOW   = 3,
	BLUE     = 4,
	MAGENTA  = 5,
	CYAN     = 6,
	WHITE    = 7,
} Color;


class ColorTerminal : public Terminal {

    char m_colorcode[sizeof("\033[0;3X;4Ym")]; //! set color in terminal: 3X = foreground, 4Y = background

public:
    ColorTerminal(Terminal::port_t port = STDOUT) : Terminal(port), m_colorcode("\033[0;3X;4Ym")  {};

	void clear(){};

	void setcolor(Color fg,  Color bg){
        m_colorcode[5] = ('0' + static_cast<uint8_t>(fg)); //! replace X for foreground color
        m_colorcode[8] = ('0' + static_cast<uint8_t>(bg)); //! replace Y for background color
        *this << m_colorcode;
    };

	void putentryat(char c, __attribute__((unused))  uint8_t color, __attribute__((unused))  size_t x, __attribute__((unused))  size_t y){
         putchar(c);
    };

};


#endif
