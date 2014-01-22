#ifndef __TERMINAL_H__
#define __TERMINAL_H__

/**
 * @file
 *
 * @ingroup posix
 *
 * \brief POSIX TERMINAL output on terminal
 */

#include <stddef.h>
#include <stdint.h>
#include "arch/generic/ostream.h"
#include <unistd.h>

class Terminal : public O_Stream<Terminal> {
    const uint16_t m_channel;
public:
    enum port_t {
        STDOUT = STDOUT_FILENO,
        STDERR = STDERR_FILENO
    };

	Terminal(port_t port) : m_channel(port) {};

	void putchar(char c);

	void puts(const char* data);
};

#endif // __TERMINAL_H__
