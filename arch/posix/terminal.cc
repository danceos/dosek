/**
 * @file
 * @ingroup posix
 * @brief POSIX Terminal output implementation
 */
#include "terminal.h"
#include <unistd.h>

void Terminal::putchar(char character) {
    write(m_channel, &character, 1);
}

void Terminal::puts(const char* data) {
	while(*data) putchar(*data++);
}
