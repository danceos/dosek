/**
 * @file
 * @ingroup i386
 * @brief Default output streams
 */

#include "os.h"
#include "output.h"

#if DEBUG

Serial kout;
Serial debug;

#else // DEBUG

Serial kout;
Null_Stream debug;

#endif // DEBUG

