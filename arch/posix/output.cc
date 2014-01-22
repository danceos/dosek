/**
 * @file
 * @ingroup posix
 * @brief Default output streams
 */

#include "output.h"

#if DEBUG

ColorTerminal kout(Terminal::STDOUT);
ColorTerminal debug(Terminal::STDERR);

#else // DEBUG

ColorTerminal kout(Terminal::STDOUT);
Null_Stream debug;

#endif // DEBUG
