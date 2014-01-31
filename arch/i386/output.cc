/**
 * @file
 * @ingroup i386
 * @brief Default output streams
 */

#include "os.h"
#include "output.h"

#if DEBUG

CGA kout;
CGA debug;

#else // DEBUG

Serial kout(Serial::COM1);
Null_Stream debug;

#endif // DEBUG

extern "C" void putchar(char c) {
	kout << c;
}

extern "C" void putstring(char *c) {
	kout << c;
}
