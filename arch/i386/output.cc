/**
 * @file
 * @ingroup i386
 * @brief Default output streams
 */

#include "os.h"
#include "output.h"

#if DEBUG

Serial kout(Serial::COM1);
Serial debug(Serial::COM1);

#else // DEBUG

Serial kout(Serial::COM1);
Null_Stream debug;

#endif // DEBUG

